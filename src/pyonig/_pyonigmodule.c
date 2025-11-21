#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "oniguruma.h"

/* Module state */
typedef struct {
    PyObject *OnigError;
} pyonig_state;

static inline pyonig_state*
get_pyonig_state(PyObject *module)
{
    void *state = PyModule_GetState(module);
    assert(state != NULL);
    return (pyonig_state *)state;
}

/* Forward declarations */
static PyTypeObject PyOnig_PatternType;
static PyTypeObject PyOnig_MatchType;
static PyTypeObject PyOnig_RegSetType;

/* Match object */
typedef struct {
    PyObject_HEAD
    PyObject *string_bytes;  /* Holds reference to original bytes */
    int *begs;
    int *ends;
    int num_regs;
} PyOnig_Match;

/* Pattern object */
typedef struct {
    PyObject_HEAD
    regex_t *regex;
    PyObject *pattern;
} PyOnig_Pattern;

/* RegSet object */
typedef struct {
    PyObject_HEAD
    OnigRegSet *regset;
    PyObject *patterns;  /* Tuple of pattern strings */
    regex_t **regexes;   /* Array of regex_t* that regset points to */
    int num_patterns;
} PyOnig_RegSet;

/* Error handling */
static void
raise_onig_error(PyObject *module, int code, OnigErrorInfo *err_info)
{
    OnigUChar s[ONIG_MAX_ERROR_MESSAGE_LEN];
    onig_error_code_to_str(s, code, err_info);
    
    pyonig_state *state = get_pyonig_state(module);
    PyErr_SetString(state->OnigError, (char *)s);
}

/* Match object methods */
static void
PyOnig_Match_dealloc(PyOnig_Match *self)
{
    Py_XDECREF(self->string_bytes);
    PyMem_Free(self->begs);
    PyMem_Free(self->ends);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

static PyObject *
PyOnig_Match_group(PyOnig_Match *self, PyObject *args)
{
    int n = 0;
    if (!PyArg_ParseTuple(args, "|i", &n)) {
        return NULL;
    }
    
    if (n < 0 || n >= self->num_regs) {
        PyErr_SetString(PyExc_IndexError, "no such group");
        return NULL;
    }
    
    const char *bytes = PyBytes_AS_STRING(self->string_bytes);
    int beg = self->begs[n];
    int end = self->ends[n];
    
    return PyUnicode_DecodeUTF8(bytes + beg, end - beg, "strict");
}

static PyObject *
PyOnig_Match_start(PyOnig_Match *self, PyObject *args)
{
    int n = 0;
    if (!PyArg_ParseTuple(args, "|i", &n)) {
        return NULL;
    }
    
    if (n < 0 || n >= self->num_regs) {
        PyErr_SetString(PyExc_IndexError, "no such group");
        return NULL;
    }
    
    const unsigned char *bytes = (const unsigned char *)PyBytes_AS_STRING(self->string_bytes);
    int beg = self->begs[n];
    
    /* Convert byte offset to character offset */
    Py_ssize_t char_offset = 0;
    for (int i = 0; i < beg; i++) {
        /* Count only start bytes of UTF-8 sequences (not continuation bytes) */
        if ((bytes[i] & 0xC0) != 0x80) {
            char_offset++;
        }
    }
    
    return PyLong_FromSsize_t(char_offset);
}

static PyObject *
PyOnig_Match_end(PyOnig_Match *self, PyObject *args)
{
    int n = 0;
    if (!PyArg_ParseTuple(args, "|i", &n)) {
        return NULL;
    }
    
    if (n < 0 || n >= self->num_regs) {
        PyErr_SetString(PyExc_IndexError, "no such group");
        return NULL;
    }
    
    const unsigned char *bytes = (const unsigned char *)PyBytes_AS_STRING(self->string_bytes);
    int end = self->ends[n];
    
    /* Convert byte offset to character offset */
    Py_ssize_t char_offset = 0;
    for (int i = 0; i < end; i++) {
        /* Count only start bytes of UTF-8 sequences (not continuation bytes) */
        if ((bytes[i] & 0xC0) != 0x80) {
            char_offset++;
        }
    }
    
    return PyLong_FromSsize_t(char_offset);
}

static PyObject *
PyOnig_Match_span(PyOnig_Match *self, PyObject *args)
{
    PyObject *start = PyOnig_Match_start(self, args);
    if (start == NULL) return NULL;
    
    PyObject *end = PyOnig_Match_end(self, args);
    if (end == NULL) {
        Py_DECREF(start);
        return NULL;
    }
    
    PyObject *result = PyTuple_Pack(2, start, end);
    Py_DECREF(start);
    Py_DECREF(end);
    return result;
}

static PyObject *
PyOnig_Match_expand(PyOnig_Match *self, PyObject *args)
{
    const char *template_str;
    if (!PyArg_ParseTuple(args, "s", &template_str)) {
        return NULL;
    }
    
    /* Simple backreference expansion */
    PyObject *result = PyUnicode_FromString(template_str);
    /* TODO: Implement proper backref expansion like _BACKREF_RE.sub */
    return result;
}

static PyObject *
PyOnig_Match_get_string(PyOnig_Match *self, void *closure)
{
    return PyUnicode_DecodeUTF8(
        PyBytes_AS_STRING(self->string_bytes),
        PyBytes_GET_SIZE(self->string_bytes),
        "strict"
    );
}

static PyObject *
PyOnig_Match_subscript(PyOnig_Match *self, PyObject *key)
{
    if (!PyLong_Check(key)) {
        PyErr_SetString(PyExc_TypeError, "indices must be integers");
        return NULL;
    }
    
    long n = PyLong_AsLong(key);
    if (n == -1 && PyErr_Occurred()) {
        return NULL;
    }
    
    return PyOnig_Match_group(self, Py_BuildValue("(i)", (int)n));
}

static PyObject *
PyOnig_Match_repr(PyOnig_Match *self)
{
    PyObject *span = PyOnig_Match_span(self, Py_BuildValue("()"));
    if (span == NULL) return NULL;
    
    PyObject *match = PyOnig_Match_group(self, Py_BuildValue("()"));
    if (match == NULL) {
        Py_DECREF(span);
        return NULL;
    }
    
    PyObject *result = PyUnicode_FromFormat(
        "<pyonig._Match span=%R match=%R>",
        span, match
    );
    
    Py_DECREF(span);
    Py_DECREF(match);
    return result;
}

static PyMethodDef PyOnig_Match_methods[] = {
    {"group", (PyCFunction)PyOnig_Match_group, METH_VARARGS,
     "Return the string matched by the RE"},
    {"start", (PyCFunction)PyOnig_Match_start, METH_VARARGS,
     "Return start index of the match"},
    {"end", (PyCFunction)PyOnig_Match_end, METH_VARARGS,
     "Return end index of the match"},
    {"span", (PyCFunction)PyOnig_Match_span, METH_VARARGS,
     "Return (start, end) tuple"},
    {"expand", (PyCFunction)PyOnig_Match_expand, METH_VARARGS,
     "Expand backreferences in template"},
    {NULL}
};

static PyGetSetDef PyOnig_Match_getset[] = {
    {"string", (getter)PyOnig_Match_get_string, NULL,
     "The string passed to match() or search()", NULL},
    {NULL}
};

static PyMappingMethods PyOnig_Match_as_mapping = {
    .mp_subscript = (binaryfunc)PyOnig_Match_subscript,
};

static PyTypeObject PyOnig_MatchType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "pyonig._Match",
    .tp_doc = "Match object",
    .tp_basicsize = sizeof(PyOnig_Match),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_dealloc = (destructor)PyOnig_Match_dealloc,
    .tp_repr = (reprfunc)PyOnig_Match_repr,
    .tp_as_mapping = &PyOnig_Match_as_mapping,
    .tp_methods = PyOnig_Match_methods,
    .tp_getset = PyOnig_Match_getset,
};

/* Pattern object methods */
static void
PyOnig_Pattern_dealloc(PyOnig_Pattern *self)
{
    if (self->regex != NULL) {
        onig_free(self->regex);
    }
    Py_XDECREF(self->pattern);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

static PyObject *
create_match_object(PyObject *string_bytes, OnigRegion *region)
{
    if (region->num_regs == 0) {
        Py_RETURN_NONE;
    }
    
    PyOnig_Match *match = PyObject_New(PyOnig_Match, &PyOnig_MatchType);
    if (match == NULL) {
        return NULL;
    }
    
    match->string_bytes = string_bytes;
    Py_INCREF(string_bytes);
    
    match->num_regs = region->num_regs;
    match->begs = PyMem_Malloc(sizeof(int) * region->num_regs);
    match->ends = PyMem_Malloc(sizeof(int) * region->num_regs);
    
    if (match->begs == NULL || match->ends == NULL) {
        Py_DECREF(match);
        return PyErr_NoMemory();
    }
    
    for (int i = 0; i < region->num_regs; i++) {
        match->begs[i] = region->beg[i];
        match->ends[i] = region->end[i];
    }
    
    return (PyObject *)match;
}

static PyObject *
PyOnig_Pattern_match(PyOnig_Pattern *self, PyObject *args, PyObject *kwargs)
{
    const char *string;
    Py_ssize_t string_len;
    int start = 0;
    int flags = ONIG_OPTION_NONE;
    
    static char *kwlist[] = {"string", "start", "flags", NULL};
    
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "s#|ii", kwlist,
                                      &string, &string_len, &start, &flags)) {
        return NULL;
    }
    
    /* Convert start from character offset to byte offset */
    int start_byte = 0;
    if (start > 0) {
        int char_count = 0;
        const unsigned char *ubytes = (const unsigned char *)string;
        for (int i = 0; i < string_len; i++) {
            /* Count only start bytes of UTF-8 sequences */
            if ((ubytes[i] & 0xC0) != 0x80) {
                char_count++;
                if (char_count == start) {
                    start_byte = i + 1;  /* Start matching AFTER this character */
                    break;
                }
            }
        }
        /* If start is at or beyond string length in characters, no match possible */
        if (char_count < start) {
            Py_RETURN_NONE;
        }
    }
    
    /* If start_byte is at or past the end, no match possible */
    if (start_byte >= string_len) {
        Py_RETURN_NONE;
    }
    
    OnigRegion *region = onig_region_new();
    if (region == NULL) {
        return PyErr_NoMemory();
    }
    
    int r = onig_match(self->regex,
                       (const OnigUChar *)string,
                       (const OnigUChar *)(string + string_len),
                       (const OnigUChar *)(string + start_byte),
                       region,
                       flags);
    
    if (r == ONIG_MISMATCH) {
        onig_region_free(region, 1);
        Py_RETURN_NONE;
    }
    
    if (r < 0) {
        onig_region_free(region, 1);
        PyObject *module = PyType_GetModule(Py_TYPE(self));
        raise_onig_error(module, r, NULL);
        return NULL;
    }
    
    PyObject *string_bytes = PyBytes_FromStringAndSize(string, string_len);
    if (string_bytes == NULL) {
        onig_region_free(region, 1);
        return NULL;
    }
    
    PyObject *match = create_match_object(string_bytes, region);
    Py_DECREF(string_bytes);
    onig_region_free(region, 1);
    
    return match;
}

static PyObject *
PyOnig_Pattern_search(PyOnig_Pattern *self, PyObject *args, PyObject *kwargs)
{
    const char *string;
    Py_ssize_t string_len;
    int start = 0;
    int flags = ONIG_OPTION_NONE;
    
    static char *kwlist[] = {"string", "start", "flags", NULL};
    
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "s#|ii", kwlist,
                                      &string, &string_len, &start, &flags)) {
        return NULL;
    }
    
    /* Convert start from character offset to byte offset */
    int start_byte = 0;
    if (start > 0) {
        int char_count = 0;
        const unsigned char *ubytes = (const unsigned char *)string;
        for (int i = 0; i < string_len; i++) {
            /* Count only start bytes of UTF-8 sequences */
            if ((ubytes[i] & 0xC0) != 0x80) {
                char_count++;
                if (char_count == start) {
                    start_byte = i + 1;  /* Start searching AFTER this character */
                    break;
                }
            }
        }
        /* If start is at or beyond string length in characters, no match possible */
        if (char_count < start) {
            Py_RETURN_NONE;
        }
    }
    
    /* If start_byte is at or past the end, no match possible */
    if (start_byte >= string_len) {
        Py_RETURN_NONE;
    }
    
    OnigRegion *region = onig_region_new();
    if (region == NULL) {
        return PyErr_NoMemory();
    }
    
    int r = onig_search(self->regex,
                        (const OnigUChar *)string,
                        (const OnigUChar *)(string + string_len),
                        (const OnigUChar *)(string + start_byte),
                        (const OnigUChar *)(string + string_len),
                        region,
                        flags);
    
    if (r == ONIG_MISMATCH) {
        onig_region_free(region, 1);
        Py_RETURN_NONE;
    }
    
    if (r < 0) {
        onig_region_free(region, 1);
        PyObject *module = PyType_GetModule(Py_TYPE(self));
        raise_onig_error(module, r, NULL);
        return NULL;
    }
    
    PyObject *string_bytes = PyBytes_FromStringAndSize(string, string_len);
    if (string_bytes == NULL) {
        onig_region_free(region, 1);
        return NULL;
    }
    
    PyObject *match = create_match_object(string_bytes, region);
    Py_DECREF(string_bytes);
    onig_region_free(region, 1);
    
    return match;
}

static PyObject *
PyOnig_Pattern_number_of_captures(PyOnig_Pattern *self, PyObject *Py_UNUSED(ignored))
{
    int n = onig_number_of_captures(self->regex);
    return PyLong_FromLong(n);
}

static PyObject *
PyOnig_Pattern_repr(PyOnig_Pattern *self)
{
    return PyUnicode_FromFormat("pyonig.compile(%R)", self->pattern);
}

static PyMethodDef PyOnig_Pattern_methods[] = {
    {"match", (PyCFunction)PyOnig_Pattern_match, METH_VARARGS | METH_KEYWORDS,
     "Match pattern at start of string"},
    {"search", (PyCFunction)PyOnig_Pattern_search, METH_VARARGS | METH_KEYWORDS,
     "Search for pattern in string"},
    {"number_of_captures", (PyCFunction)PyOnig_Pattern_number_of_captures, METH_NOARGS,
     "Return the number of capture groups"},
    {NULL}
};

static PyTypeObject PyOnig_PatternType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "pyonig._Pattern",
    .tp_doc = "Compiled regex pattern",
    .tp_basicsize = sizeof(PyOnig_Pattern),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_dealloc = (destructor)PyOnig_Pattern_dealloc,
    .tp_repr = (reprfunc)PyOnig_Pattern_repr,
    .tp_methods = PyOnig_Pattern_methods,
};

/* RegSet object methods */
static void
PyOnig_RegSet_dealloc(PyOnig_RegSet *self)
{
    if (self->regset != NULL) {
        /* onig_regset_free() frees the individual regexes too */
        onig_regset_free(self->regset);
    }
    /* Just free the array pointer, not the regex objects (regset_free does that) */
    if (self->regexes != NULL) {
        PyMem_Free(self->regexes);
    }
    Py_XDECREF(self->patterns);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

static PyObject *
PyOnig_RegSet_search(PyOnig_RegSet *self, PyObject *args, PyObject *kwargs)
{
    const char *string;
    Py_ssize_t string_len;
    int start = 0;
    int flags = ONIG_OPTION_NONE;
    
    static char *kwlist[] = {"string", "start", "flags", NULL};
    
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "s#|ii", kwlist,
                                      &string, &string_len, &start, &flags)) {
        return NULL;
    }
    
    /* Handle empty regset - always return no match */
    if (self->num_patterns == 0 || self->regset == NULL) {
        return Py_BuildValue("(iO)", -1, Py_None);
    }
    
    /* Convert start from character offset to byte offset */
    int start_byte = 0;
    if (start > 0) {
        int char_count = 0;
        const unsigned char *ubytes = (const unsigned char *)string;
        for (int i = 0; i < string_len; i++) {
            /* Count only start bytes of UTF-8 sequences */
            if ((ubytes[i] & 0xC0) != 0x80) {
                char_count++;
                if (char_count == start) {
                    start_byte = i + 1;  /* Start searching AFTER this character */
                    break;
                }
            }
        }
        /* If start is at or beyond string length in characters, no match possible */
        if (char_count < start) {
            return Py_BuildValue("(iO)", -1, Py_None);
        }
    }
    
    /* If start_byte is at or past the end, no match possible */
    if (start_byte >= string_len) {
        return Py_BuildValue("(iO)", -1, Py_None);
    }
    
    int match_pos;
    int idx = onig_regset_search(
        self->regset,
        (const OnigUChar *)string,
        (const OnigUChar *)(string + string_len),
        (const OnigUChar *)(string + start_byte),
        (const OnigUChar *)(string + string_len),
        ONIG_REGSET_POSITION_LEAD,
        flags,
        &match_pos
    );
    
    if (idx < 0) {
        /* No match */
        return Py_BuildValue("(iO)", -1, Py_None);
    }
    
    OnigRegion *region = onig_regset_get_region(self->regset, idx);
    if (region == NULL) {
        return Py_BuildValue("(iO)", -1, Py_None);
    }
    
    PyObject *string_bytes = PyBytes_FromStringAndSize(string, string_len);
    if (string_bytes == NULL) {
        return NULL;
    }
    
    PyObject *match = create_match_object(string_bytes, region);
    Py_DECREF(string_bytes);
    
    if (match == NULL) {
        return NULL;
    }
    
    PyObject *result = Py_BuildValue("(iO)", idx, match);
    Py_DECREF(match);
    return result;
}

static PyObject *
PyOnig_RegSet_repr(PyOnig_RegSet *self)
{
    PyObject *patterns_repr = PyObject_Repr(self->patterns);
    if (patterns_repr == NULL) {
        return NULL;
    }
    
    PyObject *result = PyUnicode_FromFormat("pyonig.compile_regset%S", patterns_repr);
    Py_DECREF(patterns_repr);
    return result;
}

static PyMethodDef PyOnig_RegSet_methods[] = {
    {"search", (PyCFunction)PyOnig_RegSet_search, METH_VARARGS | METH_KEYWORDS,
     "Search for any pattern in the regset"},
    {NULL}
};

static PyTypeObject PyOnig_RegSetType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "pyonig._RegSet",
    .tp_doc = "Compiled regex set",
    .tp_basicsize = sizeof(PyOnig_RegSet),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_dealloc = (destructor)PyOnig_RegSet_dealloc,
    .tp_repr = (reprfunc)PyOnig_RegSet_repr,
    .tp_methods = PyOnig_RegSet_methods,
};

/* Module functions */
static PyObject *
pyonig_compile(PyObject *module, PyObject *args)
{
    const char *pattern;
    Py_ssize_t pattern_len;
    
    if (!PyArg_ParseTuple(args, "s#", &pattern, &pattern_len)) {
        return NULL;
    }
    
    PyOnig_Pattern *self = PyObject_New(PyOnig_Pattern, &PyOnig_PatternType);
    if (self == NULL) {
        return NULL;
    }
    
    self->regex = NULL;
    self->pattern = PyUnicode_FromStringAndSize(pattern, pattern_len);
    if (self->pattern == NULL) {
        Py_DECREF(self);
        return NULL;
    }
    
    OnigErrorInfo err_info;
    int r = onig_new(&self->regex,
                     (const OnigUChar *)pattern,
                     (const OnigUChar *)(pattern + pattern_len),
                     ONIG_OPTION_NONE,
                     ONIG_ENCODING_UTF8,
                     ONIG_SYNTAX_ONIGURUMA,
                     &err_info);
    
    if (r != ONIG_NORMAL) {
        Py_DECREF(self);
        raise_onig_error(module, r, &err_info);
        return NULL;
    }
    
    return (PyObject *)self;
}

static PyObject *
pyonig_compile_regset(PyObject *module, PyObject *args)
{
    Py_ssize_t num_patterns = PyTuple_Size(args);
    if (num_patterns < 0) {
        return NULL;
    }
    
    /* Handle empty regset - create a regset that never matches */
    if (num_patterns == 0) {
        PyOnig_RegSet *self = PyObject_New(PyOnig_RegSet, &PyOnig_RegSetType);
        if (self == NULL) {
            return NULL;
        }
        self->regset = NULL;
        self->regexes = NULL;
        self->patterns = args;
        Py_INCREF(args);
        self->num_patterns = 0;
        return (PyObject *)self;
    }
    
    /* Compile individual regexes */
    regex_t **regs = PyMem_Malloc(sizeof(regex_t *) * num_patterns);
    if (regs == NULL) {
        return PyErr_NoMemory();
    }
    
    for (Py_ssize_t i = 0; i < num_patterns; i++) {
        PyObject *pattern_obj = PyTuple_GetItem(args, i);
        if (!PyUnicode_Check(pattern_obj)) {
            for (Py_ssize_t j = 0; j < i; j++) {
                onig_free(regs[j]);
            }
            PyMem_Free(regs);
            PyErr_SetString(PyExc_TypeError, "All patterns must be strings");
            return NULL;
        }
        
        const char *pattern = PyUnicode_AsUTF8(pattern_obj);
        if (pattern == NULL) {
            for (Py_ssize_t j = 0; j < i; j++) {
                onig_free(regs[j]);
            }
            PyMem_Free(regs);
            return NULL;
        }
        
        Py_ssize_t pattern_len = strlen(pattern);
        OnigErrorInfo err_info;
        
        int r = onig_new(&regs[i],
                         (const OnigUChar *)pattern,
                         (const OnigUChar *)(pattern + pattern_len),
                         ONIG_OPTION_NONE,
                         ONIG_ENCODING_UTF8,
                         ONIG_SYNTAX_ONIGURUMA,
                         &err_info);
        
        if (r != ONIG_NORMAL) {
            for (Py_ssize_t j = 0; j < i; j++) {
                onig_free(regs[j]);
            }
            PyMem_Free(regs);
            raise_onig_error(module, r, &err_info);
            return NULL;
        }
    }
    
    /* Create regset */
    PyOnig_RegSet *self = PyObject_New(PyOnig_RegSet, &PyOnig_RegSetType);
    if (self == NULL) {
        for (Py_ssize_t i = 0; i < num_patterns; i++) {
            onig_free(regs[i]);
        }
        PyMem_Free(regs);
        return NULL;
    }
    
    self->regset = NULL;
    self->regexes = NULL;
    self->patterns = NULL;
    self->num_patterns = 0;
    
    int r = onig_regset_new(&self->regset, num_patterns, regs);
    
    if (r != ONIG_NORMAL) {
        /* Clean up on error */
        for (Py_ssize_t i = 0; i < num_patterns; i++) {
            onig_free(regs[i]);
        }
        PyMem_Free(regs);
        Py_DECREF(self);
        raise_onig_error(module, r, NULL);
        return NULL;
    }
    
    /* Store the regexes array - regset needs these to stay alive */
    self->regexes = regs;
    self->patterns = args;
    Py_INCREF(args);
    self->num_patterns = (int)num_patterns;
    
    return (PyObject *)self;
}

/* Module definition */
static PyMethodDef pyonig_methods[] = {
    {"compile", pyonig_compile, METH_VARARGS,
     "Compile a regex pattern"},
    {"compile_regset", pyonig_compile_regset, METH_VARARGS,
     "Compile a set of regex patterns"},
    {NULL}
};

static int
pyonig_exec(PyObject *module)
{
    pyonig_state *state = get_pyonig_state(module);
    
    /* Initialize oniguruma */
    OnigEncoding enc = ONIG_ENCODING_UTF8;
    int r = onig_initialize(&enc, 1);
    if (r != ONIG_NORMAL) {
        PyErr_SetString(PyExc_RuntimeError, "Failed to initialize oniguruma");
        return -1;
    }
    
    /* Create exception type */
    state->OnigError = PyErr_NewException("pyonig.OnigError", PyExc_RuntimeError, NULL);
    if (state->OnigError == NULL) {
        return -1;
    }
    
    if (PyModule_AddObject(module, "OnigError", state->OnigError) < 0) {
        Py_DECREF(state->OnigError);
        return -1;
    }
    
    /* Add types */
    if (PyType_Ready(&PyOnig_PatternType) < 0) {
        return -1;
    }
    if (PyType_Ready(&PyOnig_MatchType) < 0) {
        return -1;
    }
    if (PyType_Ready(&PyOnig_RegSetType) < 0) {
        return -1;
    }
    
    /* Add version */
    const char *version = onig_version();
    if (PyModule_AddStringConstant(module, "__onig_version__", version) < 0) {
        return -1;
    }
    
    /* Add search option constants */
    if (PyModule_AddIntConstant(module, "ONIG_OPTION_NONE", ONIG_OPTION_NONE) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(module, "ONIG_OPTION_NOT_BEGIN_STRING", ONIG_OPTION_NOT_BEGIN_STRING) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(module, "ONIG_OPTION_NOT_BEGIN_POSITION", ONIG_OPTION_NOT_BEGIN_POSITION) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(module, "ONIG_OPTION_NOT_END_STRING", ONIG_OPTION_NOT_END_STRING) < 0) {
        return -1;
    }
    
    return 0;
}

static PyModuleDef_Slot pyonig_slots[] = {
    {Py_mod_exec, pyonig_exec},
    {0, NULL}
};

static struct PyModuleDef pyonigmodule = {
    PyModuleDef_HEAD_INIT,
    .m_name = "_pyonig",
    .m_doc = "Low-level bindings to oniguruma regex library",
    .m_size = sizeof(pyonig_state),
    .m_methods = pyonig_methods,
    .m_slots = pyonig_slots,
};

PyMODINIT_FUNC
PyInit__pyonig(void)
{
    return PyModuleDef_Init(&pyonigmodule);
}

