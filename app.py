"""Shiny Pokemon Hunter - Streamlit App for Pokemon Legends: Z-A and Scarlet/Violet."""

import streamlit as st
import pandas as pd
import time
from database import (
    init_db, add_shiny, get_all_shinies, get_shiny_count,
    update_hunt_progress, get_hunt_progress, get_hunt_stats, reset_hunt, delete_shiny
)
from pokeapi import (
    get_za_pokemon, get_pokemon_data, get_pokemon_sprite,
    get_types, HUNT_METHODS, get_recommended_method
)

# Page config
st.set_page_config(
    page_title="Shiny Pokemon Hunter",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark mode
st.markdown("""
<style>
    /* Dark mode adjustments */
    .stApp {
        background-color: #0e1117;
    }
    
    /* Pokemon card styling */
    .pokemon-card {
        background-color: #1e1e2e;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        transition: transform 0.2s;
    }
    .pokemon-card:hover {
        transform: scale(1.05);
    }
    
    /* Shiny badge */
    .shiny-badge {
        background: linear-gradient(45deg, #FFD700, #FFA500);
        color: #000;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 12px;
    }
    
    /* Hunt method badges */
    .method-badge {
        background-color: #2d2d44;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 11px;
    }
    
    /* Stats cards */
    .stat-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    .stat-number {
        font-size: 36px;
        font-weight: bold;
        color: #FFD700;
    }
    .stat-label {
        font-size: 14px;
        color: #aaa;
    }
</style>
""", unsafe_allow_html=True)

# Initialize database
init_db()

# Session state
if 'pokemon_list' not in st.session_state:
    with st.spinner('Loading Pokemon from Z-A Pokedex...'):
        st.session_state.pokemon_list = get_za_pokemon()
if 'show_shiny' not in st.session_state:
    st.session_state.show_shiny = False

def main():
    # Sidebar navigation
    st.sidebar.title("✨ Shiny Hunter")
    st.sidebar.markdown("### Pokemon Legends: Z-A")
    st.sidebar.markdown("*For Scarlet/Violet & Z-A*")
    
    page = st.sidebar.radio(
        "Go to",
        ["Pokedex", "Hunt Tracker", "My Shinies", "Hunt Tips", "Stats"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Game Info")
    st.sidebar.info("""
    **Pokemon Legends: Z-A**
    - Released: Oct 16, 2025
    - Region: Kalos
    - No breeding/Masuda method
    """)
    
    # Main content
    if page == "Pokedex":
        pokedex_page()
    elif page == "Hunt Tracker":
        hunt_tracker_page()
    elif page == "My Shinies":
        my_shinies_page()
    elif page == "Hunt Tips":
        hunt_tips_page()
    elif page == "Stats":
        stats_page()

def pokedex_page():
    """Pokedex view with Pokemon sprites."""
    st.title("🖼️ Pokedex")
    
    # Controls
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search = st.text_input("Search Pokemon", placeholder="e.g., Pikachu, Charizard...")
    
    with col2:
        # Shiny toggle
        st.session_state.show_shiny = st.toggle("Show Shiny Sprites", value=st.session_state.show_shiny)
    
    with col3:
        selected_type = st.selectbox("Filter by Type", ["All Types"] + get_types())
    
    # Get filtered Pokemon
    pokemon_list = st.session_state.pokemon_list
    
    if search:
        pokemon_list = [p for p in pokemon_list if search.lower() in p['name'].lower()]
    
    if selected_type != "All Types":
        # Would need to filter by type - simplified for now
        pass
    
    # Display in grid
    st.markdown(f"**Showing {len(pokemon_list)} Pokemon**")
    
    # Create columns
    cols = st.columns(6)
    
    for i, pokemon in enumerate(pokemon_list):
        with cols[i % 6]:
            sprite_url = pokemon['shiny_sprite'] if st.session_state.show_shiny else pokemon['sprite']
            
            st.markdown(f"""
            <div class="pokemon-card">
                <img src="{sprite_url}" width="96" style="image-rendering: pixelated;">
                <br>
                <strong>#{pokemon['id']} {pokemon['name']}</strong>
            </div>
            """, unsafe_allow_html=True)
            
            if st.session_state.show_shiny:
                st.markdown('<span class="shiny-badge">✨ SHINY</span>', unsafe_allow_html=True)

def hunt_tracker_page():
    """Track shiny hunting progress."""
    st.title("🎯 Hunt Tracker")
    
    # Add new hunt form
    with st.expander("➕ Start New Hunt", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Pokemon selector with search
            pokemon_names = [p['name'] for p in st.session_state.pokemon_list]
            
            # Search/filter input
            search_col, select_col = st.columns([1, 2])
            with search_col:
                pokemon_search = st.text_input("Search Pokemon", placeholder="Type to filter...")
            with select_col:
                # Filter list if search provided
                if pokemon_search:
                    filtered_names = [n for n in pokemon_names if pokemon_search.lower() in n.lower()]
                else:
                    filtered_names = pokemon_names
                selected_pokemon_name = st.selectbox("Select Pokemon", filtered_names)
            selected_pokemon = next((p for p in st.session_state.pokemon_list if p['name'] == selected_pokemon_name), None)
        
        with col2:
            hunt_method = st.selectbox("Hunt Method", list(HUNT_METHODS.keys()))
        
        with col3:
            encounters = st.number_input("Starting Encounters", min_value=0, value=0)
        
        if st.button("Start/Update Hunt"):
            if selected_pokemon:
                update_hunt_progress(
                    selected_pokemon['id'],
                    selected_pokemon['name'],
                    hunt_method,
                    encounters=encounters
                )
                st.success(f"Started hunt for {selected_pokemon['name']} using {hunt_method}!")
                time.sleep(1)
                st.rerun()
    
    st.markdown("---")
    
    # Current hunts
    st.subheader("📊 Active Hunts")
    hunts = get_hunt_progress()
    
    if not hunts:
        st.info("No active hunts. Start one above!")
        return
    
    # Display hunts in a table with proper image rendering
    from streamlit import column_config
    
    hunt_data = []
    for hunt in hunts:
        sprite = get_pokemon_sprite(hunt['pokemon_id'], shiny=True)
        hunt_data.append({
            "Sprite": sprite,
            "#": hunt['pokemon_id'],
            "Pokemon": hunt['pokemon_name'],
            "Method": hunt['method'],
            "Encounters": hunt['encounter_count'],
            "Time (min)": round(hunt['time_spent_minutes'], 1),
            "Last Updated": hunt['last_updated'][:10] if hunt['last_updated'] else "N/A"
        })
    
    df = pd.DataFrame(hunt_data)
    
    # Configure columns to show images properly
    st.dataframe(
        df,
        column_config={
            "Sprite": column_config.ImageColumn("Sprite", width="small"),
        },
        use_container_width=True,
        hide_index=True
    )
    
    # Quick update section
    st.markdown("### ⚡ Quick Update")
    
    col1, col2 = st.columns(2)
    with col1:
        hunt_options = [f"{h['pokemon_name']} ({h['method']})" for h in hunts]
        selected_hunt = st.selectbox("Select Hunt", hunt_options)
    
    with col2:
        new_encounters = st.number_input("Add Encounters", min_value=1, value=1)
    
    if st.button("Add Encounters"):
        # Find the hunt
        for hunt in hunts:
            if f"{hunt['pokemon_name']} ({hunt['method']})" == selected_hunt:
                update_hunt_progress(
                    hunt['pokemon_id'],
                    hunt['pokemon_name'],
                    hunt['method'],
                    encounters=new_encounters
                )
                st.success(f"Added {new_encounters} encounters!")
                time.sleep(1)
                st.rerun()
    
    # Reset option
    st.markdown("---")
    st.subheader("🗑️ Reset Hunt")
    if st.button("Reset Selected Hunt", type="primary"):
        for hunt in hunts:
            if f"{hunt['pokemon_name']} ({hunt['method']})" == selected_hunt:
                reset_hunt(hunt['pokemon_id'], hunt['method'])
                st.success(f"Reset hunt for {hunt['pokemon_name']}!")
                time.sleep(1)
                st.rerun()

def my_shinies_page():
    """Gallery of caught shiny Pokemon."""
    st.title("✨ My Shinies")
    
    shinies = get_all_shinies()
    shiny_count = get_shiny_count()
    
    # Stats header
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{shiny_count}</div>
            <div class="stat-label">Total Shinies</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Add new shiny
    with st.expander("➕ Record New Shiny", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Pokemon selector with search
            pokemon_names = [p['name'] for p in st.session_state.pokemon_list]
            
            # Search/filter input
            search_col, select_col = st.columns([1, 2])
            with search_col:
                pokemon_search = st.text_input("Search Pokemon", placeholder="Type to filter...")
            with select_col:
                # Filter list if search provided
                if pokemon_search:
                    filtered_names = [n for n in pokemon_names if pokemon_search.lower() in n.lower()]
                else:
                    filtered_names = pokemon_names
                selected_pokemon_name = st.selectbox("Select Pokemon", filtered_names)
            selected_pokemon = next((p for p in st.session_state.pokemon_list if p['name'] == selected_pokemon_name), None)
        
        with col2:
            hunt_method = st.selectbox("Hunt Method Used", ["Unknown"] + list(HUNT_METHODS.keys()))
        
        with col3:
            notes = st.text_input("Notes (optional)", placeholder="e.g., In Lumiose City...")
        
        if st.button("Record Shiny!"):
            if selected_pokemon:
                add_shiny(
                    selected_pokemon['id'],
                    selected_pokemon['name'],
                    hunt_method if hunt_method != "Unknown" else None,
                    notes
                )
                st.success(f"✨ Recorded {selected_pokemon['name']} as caught!")
                time.sleep(1)
                st.rerun()
    
    st.markdown("---")
    
    # Display shinies gallery
    if not shinies:
        st.info("No shinies recorded yet. Catch some shiny Pokemon!")
        return
    
    st.markdown(f"### Caught Shinies ({len(shinies)})")
    
    # Grid display
    cols = st.columns(4)
    
    for i, shiny in enumerate(shinies):
        with cols[i % 4]:
            sprite = get_pokemon_sprite(shiny['pokemon_id'], shiny=True)
            
            st.markdown(f"""
            <div class="pokemon-card" style="border: 2px solid #FFD700;">
                <img src="{sprite}" width="96" style="image-rendering: pixelated;">
                <br>
                <strong>{shiny['pokemon_name']}</strong>
                <br>
                <span style="color: #888; font-size: 11px;">{shiny['caught_date']}</span>
            </div>
            """, unsafe_allow_html=True)
            
            if shiny['hunt_method']:
                st.markdown(f'<span class="method-badge">{shiny["hunt_method"]}</span>', unsafe_allow_html=True)
            
            if shiny['notes']:
                st.caption(f"📝 {shiny['notes']}")
            
            if st.button(f"🗑️ Delete", key=f"delete_{shiny['id']}"):
                delete_shiny(shiny['id'])
                st.rerun()

def hunt_tips_page():
    """Show recommended hunting methods."""
    st.title("💡 Hunt Tips")
    
    st.markdown("""
    ## Shiny Hunting in Pokemon Legends: Z-A
    
    Welcome to the ultimate guide for shiny hunting in Pokemon Legends: Z-A! This page covers
    everything you need to know about finding shiny Pokemon in Kalos.
    
    ⚠️ **Important:** Breeding and the Masuda method are NOT available in Z-A!
    """)
    
    st.markdown("---")
    
    # Section 1: Shiny Basics
    with st.expander("🎲 Understanding Shiny Odds", expanded=True):
        st.markdown("""
        ### Base Shiny Odds
        - **Standard encounter:** 1 in ~4096 (affected by the Poké Radar in some games)
        - **With Shiny Charm:** 1 in ~1365 (if available in Z-A)
        - **With Lure:** 1 in ~2048 (multiplier varies by game)
        
        ### What Affects Shiny Rates in Z-A?
        - **Mass Outbreaks:** Increased spawn rates for certain Pokemon
        - **Tera Raids:** Different odds depending on star level
        - **Camping/Random Encounters:** Standard base odds
        - **Regional variants:** May have different odds
        """)
    
    st.markdown("---")
    
    # Section 2: Hunting Methods
    with st.expander("🏃 Hunting Methods Explained", expanded=True):
        
        st.markdown("""
        ### Respawn Method (Best for Z-A)
        The most reliable method in Z-A for stationary Pokemon.
        
        **How it works:**
        1. Find your target Pokemon
        2. Weaken or defeat it (don't catch)
        3. Use a method to force a respawn (fast travel, enter/exit building)
        4. Repeat until shiny
        
        **Best for:** Boss Pokemon, story Pokemon, stationary legendaries
        
        ---
        
        ### Fast Travel Reset
        Uses the game's fast travel system to respawn wild Pokemon.
        
        **How it works:**
        1. Find an area with your target Pokemon
        2. Save your game
        3. Fast travel to a waypoint and back
        4. Check if shiny spawned - if not, repeat
        
        **Best for:** Open area wild Pokemon, route camping
        
        ---
        
        ### Door Method
        Enter and exit buildings to respawn nearby Pokemon.
        
        **How it works:**
        1. Find building near Pokemon spawn
        2. Enter building, check Pokemon
        3. Exit - Pokemon will have respawned
        4. Repeat
        
        **Best for:** City areas with many buildings (Lumiose City!)
        
        ---
        
        ### Special Scan / Photo Spot
        In Z-A, use the camera to find rare spawns.
        
        **How it works:**
        1. Explore with camera active
        2. Look for Pokemon that react to the camera
        3. These may have increased shiny odds
        4. Great for finding version exclusives
        
        **Best for:** Finding rare spawns, photography enthusiasts
        
        ---
        
        ### Mass Outbreak Hunting
        When a mass outbreak occurs, shiny rates may be boosted.
        
        **How it works:**
        1. Monitor for mass outbreak notifications
        2. Travel to the outbreak location
        3. Defeat Pokemon to trigger respawns
        4. Check each spawn for shininess
        
        **Best for:** Farming specific species quickly
        """)
    
    st.markdown("---")
    
    # Section 3: Z-A Specific Tips
    with st.expander("🌆 Kalos-Specific Strategies", expanded=True):
        st.markdown("""
        ### Lumiose City
        The main hub of Z-A and a prime hunting location!
        
        **Hotspots:**
        - **Prism Tower:** Rare spawns around the base
        - **Café:** Interior and exterior spawns
        - **North/South Boulevard:** Route Pokemon
        - **Alleys:** Many buildings for door method
        
        **Tips:**
        - Use the elevator to access different floors quickly
        - Door method is extremely effective here
        - Save near the Pokemon you want to hunt
        
        ---
        
        ### Route Tips
        - **Route 4-7:** Good variety of Kalos natives
        - **Route 8-12:** Water types near coastlines
        - **Route 13+:** Higher-level Pokemon, more variety
        - **Snowbelle City:** Ice types (when available)
        
        ---
        
        ### Legendary Hunting
        Legendaries in Z-A require special strategies:
        
        1. **Save before EVERY encounter**
        2. **Check if they're shiny before battling** (look at overworld sprite)
        3. **Use Ace Trainer Pokemon for safe catching**
        4. **Stock up on ultra balls and timer balls**
        5. **Have a Pokemon with False Swipe and a status move**
        """)
    
    st.markdown("---")
    
    # Section 4: Type-Based Recommendations
    with st.expander("🔥 Type-Specific Hunting Tips", expanded=True):
        st.markdown("""
        ### Fire Types
        - Found in volcanic areas and sunny routes
        - Look for fire breathing from chimneys in Lumiose
        - Some fire types appear at night
        
        ### Water Types
        - Rivers and lakes have best variety
        - Use fishing for guaranteed encounters
        - Surfing Pokemon often spawn in unique forms
        
        ### Psychic Types
        - Often appear in mysterious locations
        - Some only appear after story progress
        - Check near ancient ruins
        
        ### Fairy Types
        - Kalos is home to many fairy types
        - Look near flower fields and gardens
        - Some are version-exclusive
        
        ### Dragon Types
        - Rare and powerful - hunt when you see them!
        - Often found in caves or remote areas
        - Some only appear during specific weather
        """)
    
    st.markdown("---")
    
    # Section 5: Efficiency Tips
    with st.expander("⚡ Efficiency & Quality of Life", expanded=True):
        st.markdown("""
        ### Save Time
        - **Always save before hunting** - never lose progress
        - **Use quality headphones** - shiny sparkles have unique sounds
        - **Use the bike** - faster travel = more encounters per hour
        - **Set up a hunting spot** - find a safe place to save and repeat
        
        ### Reduce Fatigue
        - Take breaks every hour
        - Use the auto-save feature strategically
        - Have a "hunting party" ready with proper abilities
        - Consider using the "catch combo" equivalent if available
        
        ### Track Your Progress
        - Use this app to log every hunt!
        - Note encounter counts for future reference
        - Track which methods work best for each Pokemon
        
        ---
        
        ### Common Mistakes to Avoid
        1. **Not saving** - Always save before starting a hunt
        2. **Catching too fast** - Check for shininess before throwing
        3. **Ignoring sounds** - Shiny Pokemon have unique cry/sound effects
        4. **Giving up too early** - Sometimes it takes thousands of encounters
        5. **Not using the right party** - Bring False Swipe and status moves
        """)
    
    st.markdown("---")
    
    # Section 6: Per-Pokemon Recommendations
    st.subheader("🎯 Recommended Methods by Pokemon")
    
    # Select a Pokemon
    pokemon_names = [p['name'] for p in st.session_state.pokemon_list]
    selected_name = st.selectbox("Select Pokemon to see recommendations", pokemon_names)
    
    if selected_name:
        selected_pokemon = next((p for p in st.session_state.pokemon_list if p['name'] == selected_name), None)
        
        if selected_pokemon:
            col1, col2 = st.columns([1, 2])
            
            with col1:
                sprite = get_pokemon_sprite(selected_pokemon['id'], shiny=True)
                st.image(sprite, width=120)
                st.markdown(f"**#{selected_pokemon['id']} {selected_pokemon['name']}**")
            
            with col2:
                st.markdown("### Recommended Methods for Z-A:")
                
                methods = get_recommended_method(selected_pokemon['name'], 'Z-A')
                for method in methods:
                    st.markdown(f"✅ **{method.replace('_', ' ').title()}**")
                    st.markdown(f"   {HUNT_METHODS.get(method, 'Standard hunting method')}")
                    st.markdown("")
    
    st.markdown("---")
    
    # Section 7: Quick Reference
    with st.expander("📋 Quick Reference Checklist", expanded=False):
        st.markdown("""
        ### Before You Hunt
        - [ ] Save your game
        - [ ] Prepare party (False Swipe, status moves, catching Pokemon)
        - [ ] Stock up on balls and potions
        - [ ] Find hunting spot
        
        ### During the Hunt
        - [ ] Check every Pokemon for shininess
        - [ ] Listen for unique sounds
        - [ ] Watch for sparkle effects
        - [ ] Keep track of encounter count in this app!
        
        ### After Catching a Shiny!
        - [ ] Celebrate! 🎉
        - [ ] Log it in this app
        - [ ] Take screenshots for memories
        - [ ] Decide: keep or trade?
        """)

def stats_page():
    """Show hunt statistics."""
    st.title("📊 Statistics")
    
    # Get stats
    shiny_count = get_shiny_count()
    hunt_stats = get_hunt_stats()
    hunts = get_hunt_progress()
    shinies = get_all_shinies()
    
    # Stats cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{shiny_count}</div>
            <div class="stat-label">Total Shinies Caught</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_encounters = hunt_stats['total_encounters'] or 0
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{total_encounters:,}</div>
            <div class="stat-label">Total Encounters</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        total_time = round(hunt_stats['total_time'] or 0, 1)
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{total_time}</div>
            <div class="stat-label">Minutes Hunting</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{hunt_stats['active_hunts'] or 0}</div>
            <div class="stat-label">Active Hunts</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Shinies by method
    if shinies:
        st.subheader("✨ Shinies by Hunt Method")
        
        method_counts = {}
        for shiny in shinies:
            method = shiny['hunt_method'] or 'Unknown'
            method_counts[method] = method_counts.get(method, 0) + 1
        
        method_df = pd.DataFrame(list(method_counts.items()), columns=['Method', 'Count'])
        method_df = method_df.sort_values('Count', ascending=False)
        
        st.bar_chart(method_df.set_index('Method'))
    
    # Hunt methods distribution
    if hunts:
        st.markdown("---")
        st.subheader("🎯 Active Hunts by Method")
        
        method_dist = {}
        for hunt in hunts:
            method = hunt['method']
            method_dist[method] = method_dist.get(method, 0) + 1
        
        method_dist_df = pd.DataFrame(list(method_dist.items()), columns=['Method', 'Count'])
        method_dist_df = method_dist_df.sort_values('Count', ascending=False)
        
        st.bar_chart(method_dist_df.set_index('Method'))
    
    # Efficiency stats
    st.markdown("---")
    st.subheader("⚡ Efficiency")
    
    if total_encounters > 0 and shiny_count > 0:
        odds = total_encounters / shiny_count
        st.metric("Average Encounters per Shiny", f"{odds:,.0f}")
    
    if shiny_count > 0:
        st.metric("Total Shinies", shiny_count)

if __name__ == "__main__":
    main()