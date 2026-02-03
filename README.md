# Sync Settings 2

> The cross-platform solution to keep your Sublime Text packages and settings in sync.

![Sync Settings](https://raw.githubusercontent.com/mfuentesg/SyncSettings/master/messages/sync-settings-logo.png)

## Installation

### Manual installation

1. Clone or download this repository.
2. Move the folder to your Sublime Text `Packages` directory.
3. Rename the folder to `SyncSettings` (or `SyncSettings 2` if you prefer, but `SyncSettings` is recommended for compatibility).

## Requirements

*   Sublime Text 4
*   Python 3.8 (Built-in to ST4)

## Getting Started

1. Open the Command Palette <kbd>Cmd</kbd> + <kbd>Shift</kbd> + <kbd>p</kbd> (OS X) or <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>p</kbd> (Linux/Windows)
2. Type `Sync Settings 2` to see available commands.
3. **If you already have a gist:**
    1. Copy `gist id` and put it in config file (`https://gist.github.com/<username>/<gist id>`) (`gist_id` property).
    2. Run `Sync Settings 2: Download` command to retrieve your backup.
4. **Else:**
    1. Create an access token [here](https://github.com/settings/tokens/new) with `gist` scope checked.
    2. Put the token in the config file (`access_token` property)
    3. Run `Sync Settings 2: Create and Upload` command

### File Format

Please note - the config file uses the JSON format. A simplified example may look like the following.

```json
{
	"access_token": "xxxxxxxxxxxxxxxxxxxxxxxxx",
	"gist_id": "xxxxxxxxxxxxxxxxxxxxxxxxx"
}
```

## Options

By default, this plugin operates over [Sublime Text](https://www.sublimetext.com) packages folder (i.e `/Users/<my_user>/Library/Application Support/Sublime Text/Packages/User`), which means, `excluded_files` and `included_files` will look for files inside that folder.

| name | type | description |
|---|---|---|
| `access_token`  | `string` | Brings write permission to Sync Settings 2 over your gists (edit, delete and create). *(This option is not required, if you only want to download your backups)* | 
| `gist_id`  | `string` | Identifier of your backup on [gist.github.com](https://gist.github.com). |
| `auto_upgrade`  | `boolean` | If is `true`, your settings will be synced with the latest settings on [gist.github.com](https://gist.github.com) when [Sublime Text](https://www.sublimetext.com) startup |
| `http_proxy`  | `string` | An HTTP proxy server to use for requests. |
| `https_proxy`  | `string` | An HTTPS proxy server to use for requests. |
| `excluded_files`  | `[]string` | In simple words, this option is a black list. Which means, every file that match with the defined pattern, will be ignored on sync. |
| `included_files`  | `[]string` | In simple words, this option is a white list. Which means, every file that match with the defined pattern, will be included on sync, even if it was included on `excluded_files` option. |

> Note: `excluded_files` and `included_files` are patterns defined as [unix shell style](https://tldp.org/LDP/GNU-Linux-Tools-Summary/html/x11655.htm).


## Commands

| command | description |
|---|---|
|**Sync Settings 2: Create and Upload**|Creates a new backup on `gist.github.com` from your local files|
|**Sync Settings 2: Delete and Create**|Deletes the remote reference of your gist and then, creates a new backup from your local files to `gist.github.com`|
|**Sync Settings 2: Upload**|Upload a backup from your local files to `gist.github.com`|
|**Sync Settings 2: Download**|Retrieves the latest version of your backup, using as reference the `gist_id` property defined in your settings file.|
|**Sync Settings 2: Delete**|Deletes the remote version of your gist, using as reference the `gist_id` property defined in your settings file. (This action is irreversible)|
|**Sync Settings 2: Show Logs**|Open a new view, with `Sync Settings 2` log file|
|**Sync Settings 2: Edit User Settings**|Open a new view, with `Sync Settings 2` user settings.|

## Contributors

Thank you for contribute to this project:

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="https://ferronrsmith.github.io/"><img src="https://avatars2.githubusercontent.com/u/159764?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Ferron H</b></sub></a><br /><a href="https://github.com/mfuentesg/SyncSettings/commits?author=ferronrsmith" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/tomahl"><img src="https://avatars0.githubusercontent.com/u/1665481?v=4?s=100" width="100px;" alt=""/><br /><sub><b>tomahl</b></sub></a><br /><a href="https://github.com/mfuentesg/SyncSettings/commits?author=tomahl" title="Code">💻</a></td>
    <td align="center"><a href="https://nachvorne.de"><img src="https://avatars3.githubusercontent.com/u/2073401?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Johannes Weber</b></sub></a><br /><a href="https://github.com/mfuentesg/SyncSettings/commits?author=JohaWeber" title="Code">💻</a></td>
    <td align="center"><a href="https://mwilliammyers.com"><img src="https://avatars1.githubusercontent.com/u/2526129?v=4?s=100" width="100px;" alt=""/><br /><sub><b>William Myers</b></sub></a><br /><a href="https://github.com/mfuentesg/SyncSettings/commits?author=mwilliammyers" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/TheSecEng"><img src="https://avatars1.githubusercontent.com/u/32599364?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Terminal</b></sub></a><br /><a href="https://github.com/mfuentesg/SyncSettings/commits?author=TheSecEng" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/mariohuq"><img src="https://avatars.githubusercontent.com/u/15021607?v=4?s=100" width="100px;" alt=""/><br /><sub><b>mariohuq</b></sub></a><br /><a href="https://github.com/mfuentesg/SyncSettings/commits?author=mariohuq" title="Code">💻</a></td>
  </tr>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

## Issues

If you are experimenting an error, or an unusual behavior. Please let me know, creating a [new issue](https://github.com/mfuentesg/SyncSettings/issues/new) appending the logs provided by the `Sync Settings 2: Show logs` command.

## Development

You are welcome to contribute to this project. 
Clone the repo and install it in your Sublime Text `Packages` directory.

## License

Sync Settings is licensed under the MIT license along with all source code.

```
Copyright (c) since 2015, Marcelo Fuentes <marceloe.fuentes@gmail.com>.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Help me keep making awesome stuff

Contribute with me, supporting this project through

[![Become a backer](https://opencollective.com/syncsettings/tiers/backer.svg?avatarHeight=50)](https://opencollective.com/syncsettings)

[![Become a backer](https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/PayPal.svg/100px-PayPal.svg.png)](https://opencollective.com/syncsettings)

<a href="https://www.buymeacoffee.com/mfuentesg" target="_blank">
   <img height="41" src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" />
</a>
