from random import randint
import math
from PIL import ImageFont, ImageDraw, Image, ImageOps


class EmojiGenerator:
    def __init__(
        self,
        color_list,
        emoji_codes,
        img_size=224,
        emoji_min_max_size=(30, 100),
        font_size=120,
    ):
        self.color_list = color_list
        self.emoji_codes = emoji_codes
        self.font_size = font_size
        self.font = ImageFont.truetype("Symbola_hint.ttf", font_size, encoding="unic")
        self.img_size = img_size
        self.emoji_min_size = min(emoji_min_max_size)
        self.emoji_max_size = max(emoji_min_max_size)
        self.emoji_rotation_max_size = math.ceil(self.emoji_max_size * (2) ** 0.5)

    def generate_emoji(self, code_point, angle, size):
        offset = 20
        mask = Image.new(
            "L", (self.font_size + offset, self.font_size + offset), color=0
        )
        mask_d = ImageDraw.Draw(mask)
        mask_d.text((0, 0), chr(code_point), font=self.font, fill=255)

        bbox = mask.getbbox()
        mask = mask.crop(bbox)
        mask = mask.resize((size, size), Image.ANTIALIAS)
        mask = mask.rotate(angle, expand=1)
        # bbox = mask.getbbox()
        # mask = mask.crop(bbox)

        return mask

    def generate_image(
        self, loc, background_color_idx, emoji_color_idx, emoji_code_idx, angle, size
    ):
        # background_color_idx = randint(0, len(self.color_list)-1)
        # emoji_color_idx = randint(0, len(self.color_list)-1)
        # while emoji_color_idx == background_color_idx:
        #     emoji_color_idx = randint(0, len(self.color_list)-1)
        # emoji_code_idx = randint(0, len(self.emoji_codes)-1)
        # angle = randint(-180,180)
        # size = randint(*self.emoji_min_max_size)
        emoji_mask = self.generate_emoji(self.emoji_codes[emoji_code_idx], angle, size)

        img = Image.new(
            "RGB",
            (self.img_size, self.img_size),
            color=self.color_list[background_color_idx],
        )
        img.paste(
            ImageOps.colorize(emoji_mask, (0, 0, 0), self.color_list[emoji_color_idx]),
            loc,
            emoji_mask,
        )

        mask = Image.new("L", (self.img_size, self.img_size), color=0)
        mask.paste(emoji_mask, loc, emoji_mask)

        return img, mask

    def generate_random_image(self):
        if self.emoji_min_size == self.emoji_max_size:
            emoji_size_range = [self.emoji_min_size]
        else:
            emoji_size_range = list(range(self.emoji_min_size, self.emoji_max_size + 1))

        background_color_idx = randint(0, len(self.color_list) - 1)
        emoji_color_idx = randint(0, len(self.color_list) - 1)
        while emoji_color_idx == background_color_idx:
            emoji_color_idx = randint(0, len(self.color_list) - 1)
        emoji_code_idx = randint(0, len(self.emoji_codes) - 1)
        angle = randint(-180, 180)
        size = emoji_size_range[randint(0, len(emoji_size_range) - 1)]
        loc = (
            randint(0, self.img_size - self.emoji_rotation_max_size),
            randint(0, self.img_size - self.emoji_rotation_max_size),
        )
        return self.generate_image(
            loc, background_color_idx, emoji_color_idx, emoji_code_idx, angle, size
        ), (emoji_code_idx, background_color_idx, emoji_color_idx, angle, loc)

    def generate_dataset(self, loc_step=1, angle_step=1, size_step=1):
        # area of image where emoji can be placed
        active_size = (self.img_size - self.emoji_rotation_max_size) // loc_step
        if self.emoji_min_size == self.emoji_max_size:
            emoji_size_range = [self.emoji_min_size]
        else:
            emoji_size_range = range(
                self.emoji_min_size, self.emoji_max_size + 1, size_step
            )

        stop = 0

        for emoji_code_idx in range(len(self.emoji_codes)):
            for background_color_idx in range(len(self.color_list)):
                for emoji_color_idx in range(len(self.color_list)):
                    if emoji_color_idx == background_color_idx:
                        continue

                    for size in emoji_size_range:
                        for angle in range(-180, 180, angle_step):
                            # get flat index of pixel location
                            for loc_idx in range(0, active_size**2, loc_step):
                                if stop > 10000:
                                    return
                                stop += 1

                                # convert loc_idx to 2d pixel location
                                scaled_loc = (
                                    active_size
                                    + (self.emoji_rotation_max_size - size) // 2
                                )
                                loc = (
                                    loc_idx // scaled_loc
                                    + scaled_loc // loc_idx * loc_step,
                                    loc_idx % scaled_loc,
                                )

                                img, mask = self.generate_image(
                                    loc,
                                    background_color_idx,
                                    emoji_color_idx,
                                    emoji_code_idx,
                                    angle,
                                    size,
                                )
                                yield img, mask, (
                                    emoji_code_idx,
                                    background_color_idx,
                                    emoji_color_idx,
                                    angle,
                                    loc,
                                )
