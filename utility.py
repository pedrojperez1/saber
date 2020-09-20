"""
This file contains helper functions for different parts of the app
"""

PLACEHOLDER_IMG = 'https://immedilet-invest.com/wp-content/uploads/2016/01/user-placeholder.jpg'

def get_channel(channels, channel_type):
    """
    Extracts channel id for given channel type from JSON response, if it exists
    Valid channel_type values include: 'Twitter', 'Facebook', 'YouTube'
    """
    matching_channel = [channel['id'] for channel in channels if channel['type'] == channel_type]
    return matching_channel[0] if matching_channel else None
