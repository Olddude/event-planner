#!/usr/bin/env python3
"""Simple test script for the new tools."""

import os
import sys
sys.path.insert(0, 'app')

from dotenv import load_dotenv
load_dotenv()

from agent import get_travel_guide, get_events, get_attractions, get_weather

def test_weather():
    print("Testing get_weather for 'Berlin' (requires OPENWEATHER_API_KEY):")
    result = get_weather("Berlin")
    print(result)
    print()

def test_travel_guide():
    print("Testing get_travel_guide for 'Berlin':")
    result = get_travel_guide("Berlin")
    print(result)
    print()

def test_events():
    print("Testing get_events for 'Berlin' (requires EVENTBRITE_API_TOKEN):")
    result = get_events("Berlin")
    print(result)
    print()

def test_attractions():
    print("Testing get_attractions for 'Berlin' (requires FOURSQUARE credentials):")
    result = get_attractions("Berlin")
    print(result)
    print()

if __name__ == "__main__":
    test_weather()
    test_travel_guide()
    test_events()
    test_attractions()
