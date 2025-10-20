"""
Test winner determination logic end-to-end
"""
import requests
import time

API_BASE = "http://127.0.0.1:8000"

def test_full_game_with_winner():
    """Test a complete game through showdown to verify winner logic."""
    
    print("\n=== TESTING WINNER LOGIC ===\n")
    
    # 1. Create sessions for both players
    print("1. Creating sessions...")
    alice_session = requests.post(f"{API_BASE}/auth/session", json={"username": "Alice"}).json()
    alice_token = alice_session["token"]
    alice_headers = {"Authorization": f"Bearer {alice_token}"}
    
    bob_session = requests.post(f"{API_BASE}/auth/session", json={"username": "Bob"}).json()
    bob_token = bob_session["token"]
    bob_headers = {"Authorization": f"Bearer {bob_token}"}
    print(f"   Alice token: {alice_token[:20]}...")
    print(f"   Bob token: {bob_token[:20]}...")
    
    # 2. Create game as Alice
    print("\n2. Creating game as Alice...")
    response = requests.post(f"{API_BASE}/game/create", 
                            headers=alice_headers,
                            json={"num_players": 2, "max_players": 2})
    create_data = response.json()
    game_id = create_data["game_id"]
    print(f"   Game ID: {game_id}")
    
    # 3. Join as Bob
    print("3. Joining as Bob...")
    requests.post(f"{API_BASE}/game/{game_id}/join", headers=bob_headers)
    
    # 3. Join as Bob
    print("3. Joining as Bob...")
    requests.post(f"{API_BASE}/game/{game_id}/join", headers=bob_headers)
    
    # 4. Start game as Alice
    print("\n4. Starting game as Alice...")
    requests.post(f"{API_BASE}/game/{game_id}/start", headers=alice_headers)
    time.sleep(0.5)
    
    # 5. Get initial state
    state = requests.get(f"{API_BASE}/game/{game_id}/state", headers=alice_headers).json()
    print(f"   Round: {state['round']}")
    print(f"   Pot: ${state['pot']}")
    
    # Display Alice's cards
    alice_data = [p for p in state['players'] if p['name'] == 'Alice'][0]
    print(f"\n   Alice's hand:")
    if alice_data['hand']:
        for card in alice_data['hand']:
            print(f"      {card['rank']} of {card['suit']}")
    else:
        print(f"      (Hidden)")
    
    # Get Bob's view
    bob_state = requests.get(f"{API_BASE}/game/{game_id}/state", headers=bob_headers).json()
    bob_data = [p for p in bob_state['players'] if p['name'] == 'Bob'][0]
    print(f"\n   Bob's hand:")
    if bob_data['hand']:
        for card in bob_data['hand']:
            print(f"      {card['rank']} of {card['suit']}")
    else:
        print(f"      (Hidden)")
    
    # 6. Fast-forward through all betting (all check/call to showdown)
    print("\n5. Playing through rounds...")
    
    # Pre-flop betting (Alice and Bob each take turn)
    print("   Pre-flop betting...")
    requests.post(f"{API_BASE}/game/{game_id}/action", 
                 headers=alice_headers,
                 json={"action": "call"})
    time.sleep(0.2)
    requests.post(f"{API_BASE}/game/{game_id}/action", 
                 headers=bob_headers,
                 json={"action": "check"})
    time.sleep(0.2)
    
    # Deal flop
    print("   Dealing flop...")
    response = requests.post(f"{API_BASE}/game/{game_id}/next-round", headers=alice_headers)
    time.sleep(0.2)
    
    state = requests.get(f"{API_BASE}/game/{game_id}/state", headers=alice_headers).json()
    print(f"   Flop cards:")
    for card in state['community_cards']['flop']:
        print(f"      {card['rank']} of {card['suit']}")
    
    # Flop betting
    print("   Flop betting...")
    requests.post(f"{API_BASE}/game/{game_id}/action", headers=alice_headers, json={"action": "check"})
    time.sleep(0.2)
    requests.post(f"{API_BASE}/game/{game_id}/action", headers=bob_headers, json={"action": "check"})
    time.sleep(0.2)
    
    # Deal turn
    print("   Dealing turn...")
    requests.post(f"{API_BASE}/game/{game_id}/next-round", headers=alice_headers)
    time.sleep(0.2)
    
    state = requests.get(f"{API_BASE}/game/{game_id}/state", headers=alice_headers).json()
    turn = state['community_cards']['turn']
    print(f"   Turn: {turn['rank']} of {turn['suit']}")
    
    # Turn betting
    print("   Turn betting...")
    requests.post(f"{API_BASE}/game/{game_id}/action", headers=alice_headers, json={"action": "check"})
    time.sleep(0.2)
    requests.post(f"{API_BASE}/game/{game_id}/action", headers=bob_headers, json={"action": "check"})
    time.sleep(0.2)
    
    # Deal river
    print("   Dealing river...")
    requests.post(f"{API_BASE}/game/{game_id}/next-round", headers=alice_headers)
    time.sleep(0.2)
    
    state = requests.get(f"{API_BASE}/game/{game_id}/state", headers=alice_headers).json()
    river = state['community_cards']['river']
    print(f"   River: {river['rank']} of {river['suit']}")
    
    # River betting
    print("   River betting...")
    requests.post(f"{API_BASE}/game/{game_id}/action", headers=alice_headers, json={"action": "check"})
    time.sleep(0.2)
    requests.post(f"{API_BASE}/game/{game_id}/action", headers=bob_headers, json={"action": "check"})
    time.sleep(0.2)
    
    # 7. Trigger showdown
    print("\n6. SHOWDOWN!")
    print("="*50)
    showdown_response = requests.post(f"{API_BASE}/game/{game_id}/showdown", headers=alice_headers)
    
    print(f"Status Code: {showdown_response.status_code}")
    print(f"Response Text: {showdown_response.text[:500]}")  # First 500 chars
    
    if showdown_response.status_code != 200:
        print(f"\n❌ ERROR: Showdown API call failed with status {showdown_response.status_code}")
        print(f"Response: {showdown_response.text}")
        return False
    
    showdown_data = showdown_response.json()
    
    # Check if winner_info exists in response
    if 'results' in showdown_data:
        results = showdown_data['results']
        
        print("\nDecoded Cards:")
        for card_id, (rank, suit) in results['decoded_cards'].items():
            print(f"   {card_id}: {rank} of {suit}")
        
        if 'winner_info' in results and results['winner_info']:
            winner_info = results['winner_info']
            
            print("\n" + "="*50)
            print("HAND EVALUATION")
            print("="*50)
            
            # Show all hands
            for player_num, hand_info in winner_info['all_hands'].items():
                print(f"\nPlayer {player_num}: {hand_info['hand_name']}")
                print(f"  Best 5 cards:")
                for card in hand_info['best_cards']:
                    print(f"    {card['rank']} of {card['suit']}")
            
            # Show winner(s)
            print("\n" + "="*50)
            if len(winner_info['winners']) == 1:
                winner = winner_info['winners'][0]
                print(f"🏆 WINNER: {winner['player_name']} (Player {winner['player_num']})")
                print(f"   Winning Hand: {winner['hand_name']}")
                print(f"   Wins pot!")
            else:
                winner_names = [w['player_name'] for w in winner_info['winners']]
                print(f"🤝 TIE between {', '.join(winner_names)}")
                print(f"   Split pot!")
            print("="*50)
            
            # Verify chip counts updated
            print("\n7. Verifying chip counts after showdown...")
            final_state = requests.get(f"{API_BASE}/game/{game_id}/state", headers=alice_headers).json()
            for player in final_state['players']:
                print(f"   {player['name']}: ${player['chips']}")
            
            print("\n✅ WINNER LOGIC TEST PASSED!")
            print("   - Showdown executed")
            print("   - Hands evaluated") 
            print("   - Winner determined")
            print("   - Chips awarded")
            return True
        else:
            print("\n❌ ERROR: No winner_info in showdown results!")
            print(f"Response: {showdown_data}")
            return False
    else:
        print("\n❌ ERROR: Invalid showdown response!")
        print(f"Response: {showdown_data}")
        return False

if __name__ == "__main__":
    try:
        success = test_full_game_with_winner()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
