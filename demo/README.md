# pyonig Demo

This directory contains sample files and a demo script to showcase pyonig's syntax highlighting capabilities.

## Sample Files

The following sample files demonstrate syntax highlighting for all supported file types:

| File | Type | Description |
|------|------|-------------|
| `sample.json` | JSON | Complex JSON structure with nested objects |
| `sample.yaml` | YAML | Kubernetes deployment configuration |
| `sample.toml` | TOML | Python project configuration (pyproject.toml style) |
| `sample.sh` | Shell | Bash deployment script with functions |
| `sample.md` | Markdown | API development guide with code blocks |
| `sample.html` | HTML | Modern dashboard with CSS and JavaScript |
| `sample.log` | Log | Application log file with various log levels |

## Demo Script

The `demo.sh` script provides an automated demonstration of all pyonig features:

### Features Demonstrated

1. **Help & Version** - Basic CLI information
2. **Theme Listing** - Show all 17 available themes
3. **Language Support** - Display supported languages
4. **File Type Highlighting** - Demonstrate each file type with different themes:
   - JSON with Monokai
   - YAML with Solarized Dark
   - TOML with Dark+
   - Shell with Abyss
   - Markdown with Quiet Light
   - HTML with Kimbie Dark
   - Log files with default theme
5. **Pipe Support** - Show `cat file | po` usage
6. **Auto-Detection** - Demonstrate content-based language detection
7. **VS Code Integration** - Explain theme auto-detection
8. **Performance** - Quick timing demonstration

### Running the Demo

#### Interactive Demo (No Recording)

```bash
# Set to not upload
export ASCIINEMA_UPLOAD=false

# Run the demo
./demo.sh
```

The script will run through all features with realistic typing simulation.

#### Record & Upload Demo

```bash
# Install asciinema if needed
pip install asciinema

# Run with recording (default)
./demo.sh
```

This will:
1. Record the entire demo to `pyonig-demo.cast`
2. Upload the recording to asciinema.org
3. Provide a shareable link

#### Options

Set environment variables before running:

```bash
# Skip asciinema upload
export ASCIINEMA_UPLOAD=false
./demo.sh

# Just run the demo function directly
source demo.sh
run_demo
```

## Manual Usage Examples

Try these commands yourself:

```bash
# Direct file highlighting
po sample.json
po --theme monokai sample.yaml
po --theme solarized-dark sample.toml

# Pipe support
cat sample.sh | po
cat sample.md | po --theme quietlight

# Auto-detection
cat sample.json | po
echo '{"test": true}' | po

# List themes and languages
po --list-themes
po --list-languages

# Different themes
po --theme abyss sample.html
po --theme kimbie-dark sample.log
po --theme tomorrow-night-blue sample.sh

# Short alias (same as 'pyonig')
po sample.json
pyonig sample.json  # Identical
```

## Theme Showcase

Each sample file is demonstrated with a different theme to showcase the variety:

1. **Monokai** - Classic dark theme (JSON)
2. **Solarized Dark** - Popular dark theme (YAML)
3. **Dark+** - VS Code default dark (TOML)
4. **Abyss** - Deep dark theme (Shell)
5. **Quiet Light** - Clean light theme (Markdown)
6. **Kimbie Dark** - Warm dark theme (HTML)
7. **Dark (default)** - Standard theme (Log)
8. **Tomorrow Night Blue** - Blue-tinted dark (pipe demo)

## Creating Your Own Samples

To create additional sample files:

1. Add the file to the `demo/` directory
2. Use a descriptive filename with proper extension
3. Add it to the demo script if desired
4. Update this README

## Demo Script Customization

Edit `demo.sh` to:

- Change typing speed (`TYPE_DELAY`)
- Adjust pause durations (`COMMAND_DELAY`, `SECTION_DELAY`)
- Add/remove sections
- Change themes used for each file type
- Modify the asciinema recording settings

## Requirements

- **pyonig** - Installed and available as `po` command
- **asciinema** - Optional, for recording demos
- **bash** - For running the demo script

## Tips

- Run in a terminal with at least 80 columns width
- Use a terminal with 256-color support for best results
- The demo takes about 3-5 minutes to complete
- Press `Ctrl+C` to interrupt the demo at any time

## Sharing

After recording with asciinema:

1. The upload link will be displayed
2. Share the link on social media, README, documentation
3. Embed in web pages using asciinema player
4. Local `.cast` file can be replayed: `asciinema play pyonig-demo.cast`

## License

All sample files in this directory are MIT licensed and provided as examples for the pyonig project.

