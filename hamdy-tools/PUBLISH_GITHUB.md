# Publishing this fork to GitHub

**Developer: Hamdy Abou El Anein**
**E-mail: hamdy.aea@protonmail.com**

The local repository is ready for publication, but GitHub repository creation and authentication are not yet configured on this machine.

1. Create a **new empty** GitHub repository at https://github.com/new.
   - Owner: `hamdyaea`
   - Repository name: `coreutils-rust`
   - Visibility: your choice
   - **Do not** initialize with README, .gitignore or license; these files already exist.

2. Install and authenticate the GitHub CLI on Manjaro, if needed:

   ```bash
   sudo pacman -S github-cli
   gh auth login
   ```

3. Publish the prepared local Git history:

   ```bash
   cd ~/Documents/coreutils-rust/source
   git remote -v
   git push -u origin main
   ```

The `origin` remote is preconfigured for `https://github.com/hamdyaea/coreutils-rust.git`.
The original uutils remote is named `upstream`, so these instructions do not push to the upstream project.

After publication, the GitHub root README.MD will render automatically. The two developer/contact comment lines will appear at the top of tracked source files in GitHub's code browser. The upstream license and original author notices remain intact.

Do not commit the generated `bin/`, `target/`, `logs/` or `reports/` folders. For a distributable binary, use the local archive in the parent directory.
