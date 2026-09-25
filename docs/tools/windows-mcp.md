# windows-mcp tools

Listed on 2026-09-26 by `scripts/mcp_probe.py`, which started the server with `uvx --python 3.13 windows-mcp serve` from `.mcp.json`.
The server reported itself as `windows-mcp` version `4.0.10` and offered 20 tools.

## App

> Open/start/launch applications and manage windows. Keywords: open, start, launch, program, application, window, foreground, focus, resize. Four modes: 'launch' (opens an application by Start Menu name), 'launch_executable' (strictly launches one executable path with separated argv and optional cwd), 'resize' (adjusts a named or active window), and 'switch' (brings a specific window into focus).

Hints: readOnlyHint: false, destructiveHint: true, idempotentHint: false, openWorldHint: false

Input schema:

```json
{
  "properties": {
    "mode": {
      "default": "launch",
      "enum": [
        "launch",
        "launch_executable",
        "resize",
        "switch"
      ],
      "type": "string"
    },
    "name": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "window_loc": {
      "anyOf": [
        {
          "items": {
            "type": "integer"
          },
          "type": "array"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "window_size": {
      "anyOf": [
        {
          "items": {
            "type": "integer"
          },
          "type": "array"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "executable": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "args": {
      "anyOf": [
        {
          "items": {
            "type": "string"
          },
          "type": "array"
        },
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "cwd": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    }
  },
  "type": "object",
  "additionalProperties": false
}
```

## DisplayInventory

> Read active display layout and DPI metadata. Reports display index, device name, monitor/work-area bounds, resolution, orientation, primary flag, effective DPI, and scale.

Hints: readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false

Input schema:

```json
{
  "properties": {},
  "type": "object",
  "additionalProperties": false
}
```

## PowerShell

> Shell/command execution. Keywords: shell, run, execute, cmd, terminal, command line, script. A comprehensive system tool for executing any PowerShell commands. Use it to navigate the file system, manage files and processes, and execute system-level operations. Capable of accessing web content (e.g., via Invoke-WebRequest), interacting with network resources, and performing complex administrative tasks. This tool provides full access to the underlying operating system capabilities, making it the primary interface for system automation, scripting, and deep system interaction.

Hints: readOnlyHint: false, destructiveHint: true, idempotentHint: false, openWorldHint: true

Input schema:

```json
{
  "properties": {
    "command": {
      "type": "string"
    },
    "timeout": {
      "default": 30,
      "type": "integer"
    }
  },
  "required": [
    "command"
  ],
  "type": "object",
  "additionalProperties": false
}
```

## FileSystem

> Manages file system operations with eight modes: 'read' (read text file contents with optional line offset/limit), 'write' (create or overwrite a file, set append=True to append), 'copy' (copy file or directory to destination), 'move' (move or rename file/directory), 'delete' (delete file or directory, set recursive=True for non-empty dirs), 'list' (list directory contents with optional pattern filter), 'search' (find files matching a glob pattern), 'info' (get file/directory metadata like size, dates, type). Relative paths are resolved from the user's Desktop folder. Use absolute paths to access other locations.

Hints: readOnlyHint: false, destructiveHint: true, idempotentHint: false, openWorldHint: false

Input schema:

```json
{
  "properties": {
    "mode": {
      "enum": [
        "read",
        "write",
        "copy",
        "move",
        "delete",
        "list",
        "search",
        "info"
      ],
      "type": "string"
    },
    "path": {
      "type": "string"
    },
    "destination": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "content": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "pattern": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "recursive": {
      "anyOf": [
        {
          "type": "boolean"
        },
        {
          "type": "string"
        }
      ],
      "default": false
    },
    "append": {
      "anyOf": [
        {
          "type": "boolean"
        },
        {
          "type": "string"
        }
      ],
      "default": false
    },
    "overwrite": {
      "anyOf": [
        {
          "type": "boolean"
        },
        {
          "type": "string"
        }
      ],
      "default": false
    },
    "offset": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "limit": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "encoding": {
      "default": "utf-8",
      "type": "string"
    },
    "show_hidden": {
      "anyOf": [
        {
          "type": "boolean"
        },
        {
          "type": "string"
        }
      ],
      "default": false
    }
  },
  "required": [
    "mode",
    "path"
  ],
  "type": "object",
  "additionalProperties": false
}
```

## Snapshot

> Take a screenshot and inspect the screen. Keywords: screenshot, screen capture, see screen, observe, look, inspect, UI elements, what's on screen. Captures complete desktop state including: system language, focused/opened windows, interactive elements (buttons, text fields, links, menus with coordinates), and scrollable areas. Set use_vision=True to include screenshot with cursor highlight. Set use_annotation=False to get a clean screenshot without bounding box overlays on UI elements (default: True, draws colored rectangles around detected elements). Set use_ui_tree=False for a faster screenshot-only snapshot when you do not need interactive or scrollable element extraction. Set width_reference_lines/height_reference_lines to overlay a grid for better spatial reasoning (make sure vision is enabled to use it). Set use_dom=True for browser content to get web page elements instead of browser UI. Set display=[0] or display=[0,1] using zero-based active Windows display indices; omit it to keep the default full-desktop behavior. Always call this first to understand the current desktop state before taking actions.

Hints: readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false

Input schema:

```json
{
  "properties": {
    "use_vision": {
      "anyOf": [
        {
          "type": "boolean"
        },
        {
          "type": "string"
        }
      ],
      "default": false
    },
    "use_dom": {
      "anyOf": [
        {
          "type": "boolean"
        },
        {
          "type": "string"
        }
      ],
      "default": false
    },
    "use_annotation": {
      "anyOf": [
        {
          "type": "boolean"
        },
        {
          "type": "string"
        }
      ],
      "default": true
    },
    "use_ui_tree": {
      "anyOf": [
        {
          "type": "boolean"
        },
        {
          "type": "string"
        }
      ],
      "default": true
    },
    "width_reference_line": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "height_reference_line": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "display": {
      "anyOf": [
        {
          "items": {
            "type": "integer"
          },
          "type": "array"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    }
  },
  "type": "object",
  "additionalProperties": false
}
```

## Screenshot

> Captures a fast screenshot-first desktop snapshot with cursor position, desktop/window summaries, and an image. This path skips UI tree extraction for speed. Use Snapshot when you need interactive element ids, scrollable regions, or browser DOM extraction. Note: the returned image may be downscaled for efficiency; when it is, multiply image coordinates by the ratio of original size to displayed size to get the actual screen coordinates for mouse actions (Click, Move, etc.).

Hints: readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false

Input schema:

```json
{
  "properties": {
    "use_annotation": {
      "anyOf": [
        {
          "type": "boolean"
        },
        {
          "type": "string"
        }
      ],
      "default": false
    },
    "width_reference_line": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "height_reference_line": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "display": {
      "anyOf": [
        {
          "items": {
            "type": "integer"
          },
          "type": "array"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    }
  },
  "type": "object",
  "additionalProperties": false
}
```

## Click

> Performs mouse clicks at specified coordinates [x, y] or passing a UI element's label/id. Supports button types: 'left' for selection/activation, 'right' for context menus, 'middle'. Supports clicks: 0=hover only (no click), 1=single click (select/focus), 2=double click (open/activate). Provide either loc or label.

Hints: readOnlyHint: false, destructiveHint: true, idempotentHint: false, openWorldHint: false

Input schema:

```json
{
  "properties": {
    "loc": {
      "anyOf": [
        {
          "items": {
            "type": "integer"
          },
          "type": "array"
        },
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "label": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "button": {
      "default": "left",
      "enum": [
        "left",
        "right",
        "middle"
      ],
      "type": "string"
    },
    "clicks": {
      "default": 1,
      "type": "integer"
    }
  },
  "type": "object",
  "additionalProperties": false
}
```

## Type

> Types text at specified coordinates [x, y] or passing a UI element's label/id. Set clear=True to clear existing text first, False to append. Set press_enter=True to submit after typing. Set caret_position to 'start' (beginning), 'end' (end), or 'idle' (default). Provide either loc or label.

Hints: readOnlyHint: false, destructiveHint: true, idempotentHint: false, openWorldHint: false

Input schema:

```json
{
  "properties": {
    "text": {
      "type": "string"
    },
    "loc": {
      "anyOf": [
        {
          "items": {
            "type": "integer"
          },
          "type": "array"
        },
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "label": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "clear": {
      "anyOf": [
        {
          "type": "boolean"
        },
        {
          "type": "string"
        }
      ],
      "default": false
    },
    "caret_position": {
      "default": "idle",
      "enum": [
        "start",
        "idle",
        "end"
      ],
      "type": "string"
    },
    "press_enter": {
      "anyOf": [
        {
          "type": "boolean"
        },
        {
          "type": "string"
        }
      ],
      "default": false
    }
  },
  "required": [
    "text"
  ],
  "type": "object",
  "additionalProperties": false
}
```

## Scroll

> Scrolls at coordinates [x, y], a UI element's label/id, or current mouse position if loc=None. Type: vertical (default) or horizontal. Direction: up/down for vertical, left/right for horizontal. wheel_times controls amount (1 wheel ≈ 3-5 lines). Use for navigating long content, lists, and web pages.

Hints: readOnlyHint: false, destructiveHint: false, idempotentHint: true, openWorldHint: false

Input schema:

```json
{
  "properties": {
    "loc": {
      "anyOf": [
        {
          "items": {
            "type": "integer"
          },
          "type": "array"
        },
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "label": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "type": {
      "default": "vertical",
      "enum": [
        "horizontal",
        "vertical"
      ],
      "type": "string"
    },
    "direction": {
      "default": "down",
      "enum": [
        "up",
        "down",
        "left",
        "right"
      ],
      "type": "string"
    },
    "wheel_times": {
      "default": 1,
      "type": "integer"
    }
  },
  "type": "object",
  "additionalProperties": false
}
```

## Move

> Moves mouse cursor to coordinates [x, y] or passing a UI element's label/id. Set drag=True to perform a drag-and-drop operation from the current mouse position to the target coordinates, or provide from_loc=[x, y] to make the drag explicit-start and atomic in one tool call. Optional duration controls bounded intermediate movement. Default (drag=False) is a simple cursor move (hover). Provide either loc or label.

Hints: readOnlyHint: false, destructiveHint: true, idempotentHint: false, openWorldHint: false

Input schema:

```json
{
  "properties": {
    "loc": {
      "anyOf": [
        {
          "items": {
            "type": "integer"
          },
          "type": "array"
        },
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "label": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "drag": {
      "anyOf": [
        {
          "type": "boolean"
        },
        {
          "type": "string"
        }
      ],
      "default": false
    },
    "from_loc": {
      "anyOf": [
        {
          "items": {
            "type": "integer"
          },
          "type": "array"
        },
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "duration": {
      "anyOf": [
        {
          "type": "number"
        },
        {
          "type": "integer"
        },
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    }
  },
  "type": "object",
  "additionalProperties": false
}
```

## Shortcut

> Executes keyboard shortcuts using key combinations separated by +. Examples: "ctrl+c" (copy), "ctrl+v" (paste), "alt+tab" (switch apps), "win+r" (Run dialog), "win" (Start menu), "ctrl+shift+esc" (Task Manager). Use for quick actions and system commands.

Hints: readOnlyHint: false, destructiveHint: true, idempotentHint: false, openWorldHint: false

Input schema:

```json
{
  "properties": {
    "shortcut": {
      "type": "string"
    }
  },
  "required": [
    "shortcut"
  ],
  "type": "object",
  "additionalProperties": false
}
```

## Wait

> Pauses execution for specified duration in seconds. Use when waiting for: applications to launch/load, UI animations to complete, page content to render, dialogs to appear, or between rapid actions. Helps ensure UI is ready before next interaction.

Hints: readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false

Input schema:

```json
{
  "properties": {
    "duration": {
      "type": "integer"
    }
  },
  "required": [
    "duration"
  ],
  "type": "object",
  "additionalProperties": false
}
```

## WaitFor

> Waits until a UI condition is satisfied, polling the Windows accessibility tree inside the tool to avoid repeated Snapshot calls. Conditions: text_exists, active_window, element_exists, element_enabled, focused_element. Provide text and/or window_name depending on the condition. Set use_dom=True for browser DOM text.

Hints: readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false

Input schema:

```json
{
  "properties": {
    "condition": {
      "type": "string"
    },
    "text": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "window_name": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "timeout": {
      "default": 10.0,
      "type": "number"
    },
    "interval": {
      "default": 0.25,
      "type": "number"
    },
    "use_dom": {
      "anyOf": [
        {
          "type": "boolean"
        },
        {
          "type": "string"
        }
      ],
      "default": false
    }
  },
  "required": [
    "condition"
  ],
  "type": "object",
  "additionalProperties": false
}
```

## Scrape

> Fetch/scrape web page content from a URL. Keywords: scrape, fetch, browse, web, URL, extract, download, read webpage. By default (use_dom=False), performs a lightweight HTTP request to the URL and returns a clean LLM-processed summary of the page to avoid context bloat. Provide query to focus extraction on specific information. Set use_dom=True to extract from the active browser tab's DOM instead (required when site blocks HTTP requests; supported in Chrome, Edge, and Firefox). Set use_sampling=False to get raw content without LLM processing.

Hints: readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: true

Input schema:

```json
{
  "properties": {
    "url": {
      "type": "string"
    },
    "query": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "use_dom": {
      "anyOf": [
        {
          "type": "boolean"
        },
        {
          "type": "string"
        }
      ],
      "default": false
    },
    "use_sampling": {
      "anyOf": [
        {
          "type": "boolean"
        },
        {
          "type": "string"
        }
      ],
      "default": true
    }
  },
  "required": [
    "url"
  ],
  "type": "object",
  "additionalProperties": false
}
```

## MultiSelect

> Selects multiple items such as files, folders, or checkboxes if press_ctrl=True, or performs multiple clicks if False. Pass locs (list of coordinates) or labels (list of UI element labels/ids).

Hints: readOnlyHint: false, destructiveHint: true, idempotentHint: false, openWorldHint: false

Input schema:

```json
{
  "properties": {
    "locs": {
      "anyOf": [
        {
          "items": {
            "items": {
              "type": "integer"
            },
            "type": "array"
          },
          "type": "array"
        },
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "labels": {
      "anyOf": [
        {
          "items": {
            "type": "integer"
          },
          "type": "array"
        },
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "press_ctrl": {
      "anyOf": [
        {
          "type": "boolean"
        },
        {
          "type": "string"
        }
      ],
      "default": true
    }
  },
  "type": "object",
  "additionalProperties": false
}
```

## MultiEdit

> Enters text into multiple input fields at specified coordinates locs=[[x,y,text], ...] or using labels=[[label,text], ...]. Provide either locs or labels.

Hints: readOnlyHint: false, destructiveHint: true, idempotentHint: false, openWorldHint: false

Input schema:

```json
{
  "properties": {
    "locs": {
      "anyOf": [
        {
          "items": {
            "items": {},
            "type": "array"
          },
          "type": "array"
        },
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "labels": {
      "anyOf": [
        {
          "items": {
            "items": {},
            "type": "array"
          },
          "type": "array"
        },
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    }
  },
  "type": "object",
  "additionalProperties": false
}
```

## Clipboard

> Copy/paste clipboard operations. Keywords: copy, paste, cut, clipboard, text transfer. Use mode="get" to read current clipboard content, mode="set" to set clipboard text.

Hints: readOnlyHint: false, destructiveHint: false, idempotentHint: true, openWorldHint: false

Input schema:

```json
{
  "properties": {
    "mode": {
      "enum": [
        "get",
        "set"
      ],
      "type": "string"
    },
    "text": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    }
  },
  "required": [
    "mode"
  ],
  "type": "object",
  "additionalProperties": false
}
```

## Process

> List and kill running processes. Keywords: task manager, running tasks, kill, terminate, stop process, PID, CPU, memory usage. Use mode="list" to list running processes with filtering and sorting options. Use mode="kill" to terminate processes by PID or name.

Hints: readOnlyHint: false, destructiveHint: true, idempotentHint: false, openWorldHint: false

Input schema:

```json
{
  "properties": {
    "mode": {
      "enum": [
        "list",
        "kill"
      ],
      "type": "string"
    },
    "name": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "pid": {
      "anyOf": [
        {
          "type": "integer"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "sort_by": {
      "default": "memory",
      "enum": [
        "memory",
        "cpu",
        "name"
      ],
      "type": "string"
    },
    "limit": {
      "default": 20,
      "type": "integer"
    },
    "force": {
      "anyOf": [
        {
          "type": "boolean"
        },
        {
          "type": "string"
        }
      ],
      "default": false
    }
  },
  "required": [
    "mode"
  ],
  "type": "object",
  "additionalProperties": false
}
```

## Notification

> Sends a Windows toast notification with a title and message.

Hints: readOnlyHint: false, destructiveHint: true, idempotentHint: false, openWorldHint: false

Input schema:

```json
{
  "properties": {
    "title": {
      "description": "The title/heading of the toast notification.",
      "type": "string"
    },
    "message": {
      "description": "The body text of the toast notification displayed below the title.",
      "type": "string"
    },
    "app_id": {
      "description": "The valid Application User Model ID of the toast notification. Required to display the notification in a specific app.",
      "type": "string"
    }
  },
  "required": [
    "title",
    "message",
    "app_id"
  ],
  "type": "object",
  "additionalProperties": false
}
```

## Registry

> Read and write the Windows Registry. Keywords: regedit, registry key, HKEY, HKCU, HKLM, Windows settings, registry value. Use mode="get" to read a value, mode="set" to create/update a value, mode="delete" to remove a value or key, mode="list" to list values and sub-keys under a path. Paths use PowerShell format (e.g. "HKCU:\Software\MyApp", "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion").

Hints: readOnlyHint: false, destructiveHint: true, idempotentHint: false, openWorldHint: false

Input schema:

```json
{
  "properties": {
    "mode": {
      "enum": [
        "get",
        "set",
        "delete",
        "list"
      ],
      "type": "string"
    },
    "path": {
      "type": "string"
    },
    "name": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "value": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ],
      "default": null
    },
    "type": {
      "default": "String",
      "enum": [
        "String",
        "ExpandString",
        "Binary",
        "DWord",
        "MultiString",
        "QWord"
      ],
      "type": "string"
    }
  },
  "required": [
    "mode",
    "path"
  ],
  "type": "object",
  "additionalProperties": false
}
```
