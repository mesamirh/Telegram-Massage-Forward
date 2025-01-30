from pyrogram import Client, filters
from dotenv import load_dotenv
import os
import logging
import glob

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %I:%M:%S %p",
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get credentials
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")

# Initialize userbot client (not bot)
app = Client("my_account", api_id=api_id, api_hash=api_hash)

# Get target groups from file
def get_target_groups():
    groups = []
    try:
        with open("groups.txt", "r") as f:
            for line in f:
                group = line.strip()
                # Remove any non-numeric characters except the minus sign
                if group.startswith("-"):
                    try:
                        group = int(group)
                        groups.append(group)
                    except ValueError:
                        logger.error(f"Invalid group ID format: {group}")
        logger.info("Loaded %d groups from groups.txt", len(groups))
        logger.info(f"Target groups: {groups}")
    except FileNotFoundError:
        logger.warning("groups.txt not found. Create it to specify target groups.")
    return groups

# Main script
def main():
    target_groups = get_target_groups()
    if not target_groups:
        logger.error("❌ No target groups specified. Please add groups to groups.txt")
        return

    @app.on_message(filters.new_chat_members)
    async def welcome_new_members(client, message):
        chat_id = message.chat.id
        logger.info(f"Received new member in group {chat_id}")
        
        if chat_id not in target_groups:
            logger.info(f"Ignoring message from non-target group: {chat_id}")
            logger.info(f"Available target groups are: {target_groups}")
            return

        logger.info(f"👤 New member joined in group: {message.chat.title}")

        try:
            # Get messages from Saved Messages
            async for saved_msg in client.get_chat_history("me", limit=1):
                # Forward the last message from Saved Messages
                forwarded_message = await client.forward_messages(
                    chat_id=chat_id,
                    from_chat_id="me",
                    message_ids=saved_msg.id
                )
                logger.info(f"✅ Welcome message forwarded to group: {message.chat.title}")
                break
        except Exception as e:
            logger.error(f"❌ Error forwarding message: {str(e)}")

    logger.info("🚀 Userbot is starting...")
    logger.info(f"📡 Monitoring {len(target_groups)} groups")
    app.run()

if __name__ == "__main__":
    main()