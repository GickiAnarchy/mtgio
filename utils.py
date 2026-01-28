import json
import os
from collections import defaultdict
from mtgsdk import Set, Card



def card_to_dict(card) -> dict:
    """
    Helper to convert an MTGSDK Card object into a clean dictionary.
    We only select the fields we actually need for the app to keep JSON size down.
    """
    return {
        "name": card.name,
        "manaCost": card.mana_cost,
        "cmc": card.cmc,
        "colors": card.colors,
        "type": card.type,
        "rarity": card.rarity,
        "set": card.set,
        "text": card.text,
        "imageUrl": card.image_url,
        "multiverseId": card.multiverse_id
    }


def get_core_sets() -> dict:
    print("Fetching list of all 'core' sets...")
    
    # 1. Fetch all core sets
    # We filter specifically for type='core'
    core_sets = Set.where(type="core").all()
    
    # Ensure directory exists for saving
    fpath = "data/core/"
    if not os.path.exists(fpath):
        os.makedirs(fpath)

    # Dictionary to hold lists of Cards, keyed by set code
    core_dict = defaultdict(list)
    
    print(f"Found {len(core_sets)} core sets. Starting card download...")

    # 2. Process and Group
    for s in core_sets:
        print(f"Fetching cards for set: {s.name} ({s.code})...")
        
        try:
            # Fetch cards specifically for this set code
            # Note: This performs a network request for every set.
            cards_in_set = Card.where(set=s.code).all()
            
            # 3. Serialize and Add to Dictionary
            # We use a list comprehension to convert every Card object to a dict
            serialized_cards = [card_to_dict(c) for c in cards_in_set]
            
            # Store in our master dictionary
            core_dict[s.code] = serialized_cards
            
            # OPTIONAL: Save individual set files immediately (safer if script crashes)
            with open(os.path.join(fpath, f"{s.code}.json"), 'w', encoding='utf-8') as f:
                json.dump(serialized_cards, f, indent=4, ensure_ascii=False)

        except Exception as e:
            print(f"Error processing set {s.code}: {e}")

    return core_dict


def get_funny_sets() -> dict:
    print("Fetching list of all 'funny' sets...")
    
    # 1. Fetch all funny sets
    # We filter specifically for type='funny'
    funny_sets = Set.where(type="funny").all()
    
    # Ensure directory exists for saving
    fpath = "data/funny/"
    if not os.path.exists(fpath):
        os.makedirs(fpath)

    # Dictionary to hold lists of Cards, keyed by set code
    funny_dict = defaultdict(list)
    
    print(f"Found {len(funny_sets)} funny sets. Starting card download...")

    # 2. Process and Group
    for s in funny_sets:
        print(f"Fetching cards for set: {s.name} ({s.code})...")
        
        try:
            # Fetch cards specifically for this set code
            # Note: This performs a network request for every set.
            cards_in_set = Card.where(set=s.code).all()
            
            # 3. Serialize and Add to Dictionary
            # We use a list comprehension to convert every Card object to a dict
            serialized_cards = [card_to_dict(c) for c in cards_in_set]
            
            # Store in our master dictionary
            funny_dict[s.code] = serialized_cards
            
            # OPTIONAL: Save individual set files immediately (safer if script crashes)
            with open(os.path.join(fpath, f"{s.code}.json"), 'w', encoding='utf-8') as f:
                json.dump(serialized_cards, f, indent=4, ensure_ascii=False)

        except Exception as e:
            print(f"Error processing set {s.code}: {e}")

    return funny_dict


def get_expansion_sets() -> dict:
    print("Fetching list of all 'expansion' sets...")
    
    # 1. Fetch all expansion sets
    # We filter specifically for type='expansion'
    expansion_sets = Set.where(type="expansion").all()
    
    # Ensure directory exists for saving
    fpath = "data/expansion/"
    if not os.path.exists(fpath):
        os.makedirs(fpath)
    
    # Dictionary to hold lists of Cards, keyed by set code
    expansion_dict = defaultdict(list)
    
    print(f"Found {len(expansion_sets)} expansion sets. Starting card download...")
    
    # 2. Process and Group
    for s in expansion_sets:
        print(f"Fetching cards for set: {s.name} ({s.code})...")
        
        try:
            # Fetch cards specifically for this set code
            # Note: This performs a network request for every set.
            cards_in_set = Card.where(set=s.code).all()
            
            # 3. Serialize and Add to Dictionary
            # We use a list comprehension to convert every Card object to a dict
            serialized_cards = [card_to_dict(c) for c in cards_in_set]
            
            # Store in our master dictionary
            expansion_dict[s.code] = serialized_cards
            
            # OPTIONAL: Save individual set files immediately (safer if script crashes)
            with open(os.path.join(fpath, f"{s.code}.json"), 'w', encoding='utf-8') as f:
                json.dump(serialized_cards, f, indent=4, ensure_ascii=False)

        except Exception as e:
            print(f"Error processing set {s.code}: {e}")

    return expansion_dict


def generate_set_files():
    """
    Pulls all MTG Sets from online API and writes them to file according to year of release.
    """
    
    print("Fetching all sets from API... (This may take a moment)")
    
    try:
        # 1. Fetch all sets
        # The SDK handles pagination automatically with .all()
        all_sets = Set.all()
        
        # Dictionary to hold lists of sets, keyed by year
        sets_by_year = defaultdict(list)
        
        print(f"Successfully fetched {len(all_sets)} sets. Processing...")

        # 2. Process and Group
        for s in all_sets:
            # Check if release_date exists
            if not s.release_date:
                continue

            # Extract the year (Format is usually YYYY-MM-DD)
            year = s.release_date.split('-')[0]
            
            # Create a clean dictionary for the JSON output
            # We explicitly map fields to ensure JSON compatibility
            set_data = {
                "name": s.name,
                "code": s.code,
                "releaseDate": s.release_date,
                "type": s.type,
                "block": getattr(s, 'block', None), # Some sets might not belong to a block
                "onlineOnly": getattr(s, 'online_only', False)
            }
            
            sets_by_year[year].append(set_data)

        # 3. Write to files
        # Create a directory to keep things organized
        output_dir = "mtg_sets_by_year"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for year, set_list in sets_by_year.items():
            filename = os.path.join(output_dir, f"{year}.json")
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(set_list, f, indent=4, ensure_ascii=False)
            
            print(f"Created {filename} with {len(set_list)} sets.")

        print("\nDone! All files generated in the 'mtg_sets_by_year' folder.")

    except Exception as e:
        print(f"An error occurred: {e}")




if __name__ == "__main__":
    get_funny_sets()
    get_expansion_sets()