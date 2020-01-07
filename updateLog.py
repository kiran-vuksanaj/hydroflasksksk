import datetime, subprocess

print("Please enter your name:")
print("Format: firstnameL")
name = input()

print("\n")
print("Please enter your update:")
update = input()

timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

try:
    subprocess.run(['git', 'pull']).check_returncode()
    with open("./doc/devlog.txt", "a") as devlog:
        devlog.write("\n" + name + " -- " + timestamp + "\n")
        devlog.write(update+"\n")
    subprocess.run(['git', 'add', '.'])
    subprocess.run(['git', 'commit', '-m', name + ': ' + update])
    subprocess.run(['git', 'push'])
except subprocess.CalledProcessError:
    print("Error pulling changes, please fix merge conflicts and try again.")
