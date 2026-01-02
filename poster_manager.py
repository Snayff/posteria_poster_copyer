import os
import shutil
import yaml
import logging
from pathlib import Path
from tqdm import tqdm

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def load_config(config_path='config.yaml'):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def find_matching_film(poster_title, films):
    film_titles = [f.rsplit(' [', 1)[0] for f in films]
    matches = [films[i] for i, ft in enumerate(film_titles) if poster_title in ft]
    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        logging.warning(f"Multiple matches for '{poster_title}': {matches}")
        return None
    else:
        logging.warning(f"No match found for '{poster_title}'")
        return None

def process_poster(poster_path, film_path, dry_run):
    poster_file = Path(poster_path)
    film_dir = Path(film_path)

    if dry_run:
        poster_jpg = film_dir / "poster.jpg"
        action = "copy and rename to poster.jpg"
        if poster_jpg.exists():
            action += " (delete existing poster.jpg)"
        print(f"[DRY RUN] {poster_file.name} -> {film_dir.name}: {action}")
    else:
        shutil.copy(poster_file, film_dir)
        copied_file = film_dir / poster_file.name
        poster_jpg = film_dir / "poster.jpg"
        if poster_jpg.exists():
            os.remove(poster_jpg)
        copied_file.rename(poster_jpg)
        logging.info(f"Processed {poster_file.name} -> {film_path}/poster.jpg")

def main():
    config = load_config()
    posters_path = Path(config['posters_path'])
    films_path = Path(config['films_path'])
    dry_run = config['dry_run']

    if not posters_path.exists() or not films_path.exists():
        logging.error("Posters or films path does not exist.")
        return

    posters = list(posters_path.glob('*.jpg'))
    films = [f.name for f in films_path.iterdir() if f.is_dir()]

    matched = 0
    skipped = 0
    for poster in tqdm(posters, desc="Processing posters"):
        poster_base = poster.stem
        poster_title = poster_base.split(' [')[0]
        matching_film = find_matching_film(poster_title, films)
        if matching_film:
            film_full_path = films_path / matching_film
            process_poster(poster, film_full_path, dry_run)
            matched += 1
        else:
            skipped += 1

    print(f"Summary: Processed {len(posters)} posters, {matched} matched and processed, {skipped} skipped.")

if __name__ == "__main__":
    main()
