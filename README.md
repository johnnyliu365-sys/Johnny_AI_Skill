A local-first control plane for structured, traceable and safer AI-assisted software development with Codex and Claude Code.
## 安裝前先確認

先確認電腦有：

* Git：`git --version`
* Python 3.11：`py -3.11 --version`
* 如果要用 Level 1，還需要先安裝 Claude Code

## 安裝時最容易踩的坑

**不要在任何 Git repository 裡執行安裝。**

很多人會直接把安裝檔丟進自己的專案資料夾再雙擊，但這樣安裝器會直接擋掉：

`INSTALL_BLOCKED_INSIDE_REPOSITORY`

請另外找一個普通資料夾，例如下載資料夾或桌面上的暫存資料夾。

## Level 1：只安裝 Claude Code Plugin

在終端機執行：

```bash
claude plugin marketplace add johnnyliu365-sys/Johnny_AI_Skill
claude plugin install johnny-ai-skill@johnny-ai-skill --scope user
```

完成後重新開啟 Claude Code session，或輸入：

```text
/reload-plugins
```

## Level 2：安裝完整 Router Runtime

1. 把 `johnny-install.cmd` 和 release 的 zip 下載到**同一個資料夾**
2. 確認這個資料夾**不是 Git repository**
3. 雙擊 `johnny-install.cmd`
4. 安裝器會先檢查 zip 的 SHA-256
5. 驗證通過後會顯示要安裝的內容
6. 確認沒問題後，手動輸入：

```text
INSTALL
```

才會正式開始安裝。

## 確認有沒有裝成功

執行：

```powershell
powershell -ExecutionPolicy Bypass -File "$env:LOCALAPPDATA\JohnnyRouter\launcher\johnny-router.ps1" status
```

看到：

```json
"status": "OK"
```

就代表安裝完成。

## 常見錯誤

| 錯誤代碼                                | 怎麼處理                                |
| ----------------------------------- | ----------------------------------- |
| `INSTALL_BLOCKED_INSIDE_REPOSITORY` | 換到不是 Git repo 的資料夾再執行               |
| `PYTHON_311_UNAVAILABLE`            | 安裝 Python 3.11                      |
| `GIT_UNAVAILABLE`                   | 安裝 Git                              |
| `BUNDLE_NOT_FOUND`                  | 確認 zip 和 `johnny-install.cmd` 放在同一層 |
| `DIGEST_MISMATCH`                   | 檔案可能不完整，重新下載                        |
| `USER_DECLINED`                     | 需要手動輸入 `INSTALL`                    |
| `VENV_ALREADY_PRESENT`              | 已經安裝過，先 uninstall 再重裝               |
