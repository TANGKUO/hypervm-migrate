## Disclaimer

All this code is very much hacked together to try and get things working in a reasonably reliable manner. It may have flaws, may be unpolished, or not even fully automated. Since pretty much noone uses HyperVM anymore anyway, I don't think this is too much of an issue.

**Do not under any circumstances attempt to use this code *without* first backing up all user and VPS data.** Use at your own risk.

This is going to take some attention and time to set up properly, and you'll be on your own for parts of it... but honestly, there's not really an alternative for mass HyperVM transfers.

## Caveats

* HyperVM is terrible. It may arbitrarily fail, and you may never find out why or how. Prepare to watch your migration status at regular intervals, taking over any transfers manually where necessary.
* **You cannot skip transfers.** While messing around with the database may give a similar result, it's not recommended. When a transfer fails, complete it manually and mark it as done manually (using `mark_done.py`).
* **Do not under any circumstances manually transfer a VPS to a new node during the migration process.** This will mess up the state in the migration database. Wait with manual migrations until the automated migrations have completed.
* To prevent issues, the migration towards a node will be suspended entirely when a failure happens. It will only resume after you have indicated that the transfer has been completed manually. Other nodes will continue migrating in the meantime.
* This usage guide was written afterwards. Doing this migration was largely a matter of trial and error, and I might be missing steps here. If you're stuck, you can always send an e-mail to admin@cryto.net, but I might simply not remember how I did something.
* **You should use the `admin` HyperVM user, and *not* an auxiliary account.**
* Reseller VPSes will fail to transfer and require manual transfer. The cause is apparently that a reseller VPS transfer has to be initiated from a different page, but I have not had the time to try and fix this.

## Requirements

* HyperVM.
* A HTTPd + PHP + MySQL setup.
* The Python `oursql` module.

## Data you need

1. A CSV database dump in the format `username,vpsid,currentnode,plan`.
2. A CSV database dump in the format `vpsid,email`.
3. A CSV list of VPS sizes in the format `size,vpsid`. You can gather this through running `du -sh /vz/private/*` on each node, creating one giant list out of results from all nodes, and replacing tabs with commas.

## Setup instructions for environment

1. Set up a new VPS (that will not be transfered!) with the environment as listed in the Requirements section.
2. Create a new database, and import `structure.sql` into it.
3. Clone the repository, and be sure to move everything in `public_html` to your document root for the HTTPd.
4. Edit the `.php` files in the document root to set the database configuration.

## Setup instructions for migration schedule

1. Create a file named `input.csv` with the data from the first database dump.
2. Modify sort.py. The `locations` variable holds a structure with all the nodes for the current locations. `new_servers` holds a structure defining how many new nodes exist for each 'category' in each location. In the existing script, these are marked as 12, 34, and 56, but you can use any numeric value here. If you increase or decrease the amount of categories, be sure to change the code elsewhere to reflect this. Change the code from line 43 to 48, to sort the plans into the right categories. Change the hostname in line 73 to reflect your hostname format.
3. Run sort.py, redirecting stdout to a file named `sorted.csv`. You now have your existing VPSes planned uniformly across the number of nodes you have for each category in each location.
4. Edit `schedule.py`, `emails.py`, `reorder_size.py`, `failed.py`, `status.py`, `mark_done.py`, and `run.py`, and set the correct database configuration in each.
5. Run `schedule.py`.
6. Create a new file containing the second database dump as `emails.csv`.
7. Run `emails.py`.
8. Create a new file containing the third database dump as `sizes.csv`.
9. Run `reorder_size.py`.

## Other setup stuff

1. Edit `run.py` to use the correct SMTP login details, sender address, and panel login details.
2. Edit the e-mail templates in `run.py` to reflect what you want to send to your users.
3. Edit `report.php` to set a 'reporting key' that is used by the HyperVM panel to authenticate itself to your reporting script.
4. Back up the original `livemigrate.php` and `switchserver.php` in `hypervm/bin/common/` (you'll need to restore these after the migration!).
5. Copy the patched files from the `patch` directory into the `hypervm/bin/common` directory.
6. Edit the reporting key in the patched `livemigrate.php` and `switchserver.php` files. Note that it has to be replaced in two places in each of the files!
7. Edit the hostname that the patched migration scripts should report to.

## Running the migration

* The migration process is largely automatic. You do need to pay regular attention to the status to resolve any issues.
* `run.py` will start the migration. Using the `--resume` flag will make it skip the initial notification e-mail phase. Do this when for whatever reason the script has terminated, and you wish to restart it.
* If a transfer fails (or gets stuck in the 'busy' phase), ensure that it has finished transfering and manually transfer it if required. Afterwards, run `mark_done.py` with the name of the target node as first parameter. It will assume that the currently transfering/failed VPS has finished migrating, send a success e-mail, and move on to the next.
* `status.py` will give you a human-readable overview of the current status for each node.
* `failed.py` will give you an overview of the relevant information for all transfers that are in the 'failed' state, and need manual attention.
* All sent e-mails are logged to `email.txt`.

## License

All this, except for obviously the BlueVM logo, is licensed under the [WTFPL](http://wtfpl.net/). Reuse as you wish. [Donations are very much appreciated](http://cryto.net/~joepie91/donate.html).
