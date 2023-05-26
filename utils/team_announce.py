import random
import io
import aiohttp
from PIL import Image, ImageSequence

async def get_avatar_image(guild, user_id, size):
    member = guild.get_member(user_id)
    if member is None:
        return None, None

    avatar_url = member.avatar.url
    async with aiohttp.ClientSession() as session:
        async with session.get(avatar_url) as response:
            image_data = await response.read()

    image = Image.open(io.BytesIO(image_data))

    if image.format == 'GIF':
        frames = ImageSequence.Iterator(image)
        resized_frames = [frame.resize((size, size)) for frame in frames]
        return resized_frames, 'GIF'
    else:
        if image.mode == 'RGBA':
            alpha = image.split()[3]
            bg = Image.new("RGB", image.size, (255, 255, 255))
            bg.paste(image, mask=alpha)
            image = bg
        return [image.resize((size, size))], 'PNG'


def add_frames(avatar_frames, pos, group_photo, overlay_image, max_frames):
    frames = []
    num_frames = len(avatar_frames)
    for i in range(max_frames):
        frame = avatar_frames[i % num_frames]
        temp_group_photo = group_photo.copy()
        temp_group_photo.paste(frame, (int(pos[0] - frame.width / 2), int(pos[1] - frame.height / 2)))
        # temp_group_photo.alpha_composite(overlay_image)
        frames.append(temp_group_photo)
    return frames


async def create_team_photo(ctx, photo_setups, member_ids):
    matching_elements = [item for item in photo_setups if len(item[1]) == len(member_ids)]
    if matching_elements:
        photo_setup = random.choice(matching_elements)
        if photo_setup is not None:
            await process_photo(ctx, photo_setup, member_ids)


async def process_photo(ctx, photo_setup, member_ids):
    photo_url = photo_setup[0]
    photo_url = photo_url.strip()
    async with aiohttp.ClientSession() as session:
        async with session.get(photo_url) as response:
            image_data = await response.read()

    avatarPhotoPositionList = photo_setup[1]
    group_photo = Image.new("RGBA", (950, 512), (0, 0, 0, 0))
    overlay_image = Image.open(io.BytesIO(image_data)).convert("RGBA")
    overlay_image = overlay_image.resize(group_photo.size)

    avatars = []
    max_frames = 0

    for index, pos in enumerate(avatarPhotoPositionList):
        avatar_frames, _ = await get_avatar_image(ctx.guild, member_ids[index], pos[2])
        if avatar_frames is None:
            await ctx.send(f"Member with ID {member_ids[index]} not found.")
            return
        avatars.append((avatar_frames, pos))
        max_frames = max(max_frames, len(avatar_frames))

    all_frames = []
    for avatar_frames, pos in avatars:
        frames = add_frames(avatar_frames, pos, group_photo, overlay_image, max_frames)
        all_frames.append(frames)

    frames = []
    for frame_set in zip(*all_frames):
        composite_frame = frame_set[0]
        for frame in frame_set[1:]:
            composite_frame = Image.alpha_composite(composite_frame, frame)
        composite_frame = Image.alpha_composite(composite_frame, overlay_image)
        frames.append(composite_frame)

    frames[0].save("group_photo.gif", save_all=True, append_images=frames[1:], loop=0)

