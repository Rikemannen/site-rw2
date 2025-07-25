# Exercise site!
A useful (?) site with a lot of features for learning stuff.
## Brief feature list
- Exercises:
    - Creating exercises
    - Editing them
    - Doing attempts at them
    - Statistics: attempts, finishes, likes.
- Users/accounts:
    - Users have profiles
    - Users can edit profiles :O
    - Users can make exercises, verified users do not need to have theirs verified
    - Users can chat in the public chat
    - Users can equip emblems that they own to get a cool color on their name!
- Admins:
    - Admins can do moderating and stuff,
    - Change most user data
    - Change most exercise data
    - Change most emblem data
    - Well, change most data of most things
## Installation/Setup
1. Clone the repo:
```bash
git clone https://github.com/Rikemannen/learning-site.git
```
2. Get the paths correct (cd into repo):
```bash
cd ./learning-site/
```
3. Setup python stuff:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
4. Set secret key:
```bash
export SECRET_KEY='super-secret-key'
```
5. Install tailwindcss:
```bash
npm install tailwindcss @tailwindcss/cli
```
6. Start the tailwind build process:
```bash
npx @tailwindcss/cli -i ./app/static/input.css -o ./app/static/output.css --watch
```
7. (In a new window/tab) Start the flask server:
```bash
python3 run.py
```
8. Go to localhost:5000
### 9. Thx for using!