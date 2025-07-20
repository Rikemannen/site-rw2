"""Handles all file related operations."""

import os
import json

def create_exercise_files(exercise_id, html_data, json_data):
    """
    Create necessary files for an exercise to work correctly.
    
    :param exercise_id: ID of the exercise.
    :param html_data: HTML content to be saved.
    :param json_data: JSON content to be saved.
    """

    html_dir_path = os.path.join("app", "templates", "exercises", str(exercise_id))
    os.makedirs(html_dir_path, exist_ok=True)

    html_file_path = os.path.join(html_dir_path, "exercise.html")
    with open(html_file_path, "w", encoding="utf-8") as html_file:
        html_file.write(html_data)

    json_dir_path = os.path.join("app", "exercises", str(exercise_id))
    os.makedirs(json_dir_path, exist_ok=True)

    json_file_path = os.path.join(json_dir_path, "answers.json")
    with open(json_file_path, "w", encoding="utf-8") as json_file:
        json.dump(json_data, json_file)

def get_exercise_answers(exercise_id):
    """Retrieve the answers for a given exercise."""

    dir_path = os.path.join("app", "exercises", str(exercise_id), "answers.json")
    if not os.path.exists(dir_path):
        return None

    with open(dir_path, "r", encoding="utf-8") as json_file:
        try:
            return json.load(json_file)
        except IOError as e:
            print(f"Error reading answers for exercise {exercise_id}: {e}")
            return None

def get_exercise_html(exercise):
    """Retrieve the raw html for a given exercise."""
    dir_path = os.path.join("app", "templates", "exercises", str(exercise.id), "exercise.html")
    if not os.path.exists(dir_path) or not exercise:
        return None
    
    with open(dir_path, "r", encoding="utf-8") as f:
        try:
            return f.read()
        except IOError as e:
            print(f"Error reading html file, {exercise.id}: {e}")

def delete_exercise_files(exercise_id):
    """Delete the exercise files and directory."""

    html_dir_path = os.path.join("app", "templates", "exercises", str(exercise_id))
    json_dir_path = os.path.join("app", "exercises", str(exercise_id))

    if os.path.exists(html_dir_path):
        os.rmdir(html_dir_path)
    if os.path.exists(json_dir_path):
        os.rmdir(json_dir_path)