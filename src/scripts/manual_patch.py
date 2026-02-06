import json
import os

JSON_PATH = "src/database/data/planets_in_signs.json"

# Manual updates based on Lines 660-1000 of Binder1.txt
PATCHES = {
    # SATURN
    "SATURN_ARIES_DAY": "Saturn in Aries... is in his Fall. Means in some cases the state of the body, and in others, the general working of the soul... or possessions, and sometimes can mean friends... or the quality of one's death. Skillful, with much hair, of good stature, his gaze directed at the earth... with foul speech.",
    "SATURN_ARIES_NIGHT": "Saturn in Aries... is in his Fall. Means in some cases the state of the body... or the quality of one's death. (Valens/Lilly)",
    "SATURN_TAURUS_DAY": "Saturn in Taurus... is Peregrine. He is envious, covetous, jealous and mistrustful, timorous... of a profound cogitation. (Lilly)",
    "SATURN_TAURUS_NIGHT": "Saturn in Taurus... is Peregrine. He is envious, covetous, jealous and mistrustful, timorous... of a profound cogitation. (Lilly)",
    "SATURN_GEMINI_DAY": "Condition: Peregrine. Saturn makes those born under him petty, malicious... solitary, deceitful... secretive in their trickery. (Valens General Nature)",
    "SATURN_GEMINI_NIGHT": "Condition: Peregrine. Saturn makes those born under him petty, malicious... solitary, deceitful... secretive in their trickery. (Valens General Nature)",
    "SATURN_CANCER_DAY": "Saturn in Cancer... is in his Detriment. Denotes the native to be of a weak constitution, subject to cold and moist diseases... dropsy, pain in the tendons. (Lilly/Valens)",
    "SATURN_CANCER_NIGHT": "Saturn in Cancer... is in his Detriment. Denotes the native to be of a weak constitution, subject to cold and moist diseases... dropsy, pain in the tendons. (Lilly/Valens)",
    "SATURN_LEO_DAY": "Saturn in Leo... is in his Detriment. Enemies by opposition of Houses. The passage of Saturn through Leo... produces all kinds of disasters.",
    "SATURN_LEO_NIGHT": "Saturn in Leo... is in his Detriment. Enemies by opposition of Houses. The passage of Saturn through Leo... produces all kinds of disasters.",
    "SATURN_VIRGO_DAY": "The passage of Saturn through... Virgo... produces all kinds of disasters. He makes farmers and gardeners because he rules the soil. (Valens)",
    "SATURN_VIRGO_NIGHT": "The passage of Saturn through... Virgo... produces all kinds of disasters. He makes farmers and gardeners because he rules the soil. (Valens)",
    "SATURN_LIBRA_DAY": "Saturn has its exaltation in Libra. Produces all kinds of disasters [if afflicted].",
    "SATURN_LIBRA_NIGHT": "Saturn has its exaltation in Libra. Produces all kinds of disasters [if afflicted].",
    "SATURN_SCORPIO_DAY": "Condition: Peregrine. Saturn makes those born under him petty, malicious... solitary, deceitful. (Valens General Nature)",
    "SATURN_SCORPIO_NIGHT": "Condition: Peregrine. Saturn makes those born under him petty, malicious... solitary, deceitful. (Valens General Nature)",
    "SATURN_SAGITTARIUS_DAY": "Condition: Peregrine. Saturn makes those born under him petty, malicious... solitary, deceitful. (Valens General Nature)",
    "SATURN_SAGITTARIUS_NIGHT": "Condition: Peregrine. Saturn makes those born under him petty, malicious... solitary, deceitful. (Valens General Nature)",
    "SATURN_CAPRICORN_DAY": "Saturn... its traditional domiciles are said to be Capricorn and Aquarius. Saturn in Capricorn... getting out of the sign towards Aquarius in which earthquakes are frequent.",
    "SATURN_CAPRICORN_NIGHT": "Saturn... its traditional domiciles are said to be Capricorn and Aquarius.",
    "SATURN_AQUARIUS_DAY": "The passage through Aquarius is the cause of great catastrophes, something justified by the fact that Aquarius is one of the domiciles of Saturn. Signifies structure, law, restriction.",
    "SATURN_AQUARIUS_NIGHT": "The passage through Aquarius is the cause of great catastrophes, something justified by the fact that Aquarius is one of the domiciles of Saturn. Signifies structure, law, restriction.",
    "SATURN_PISCES_DAY": "The passage through Aquarius [to Pisces] is the cause of great catastrophes... Peasants will suffer hunger.",
    "SATURN_PISCES_NIGHT": "The passage through Aquarius [to Pisces] is the cause of great catastrophes... Peasants will suffer hunger.",

    # JUPITER
    "JUPITER_ARIES_DAY": "Jupiter in Aries [is in] the Triplicity of the Sun by day. Rules the fiery triplicity.",
    "JUPITER_ARIES_NIGHT": "Jupiter rules the fiery triplicity by night.",
    "JUPITER_TAURUS_DAY": "Jupiter indicates childbearing, engendering, desire, loves... prosperity, salaries, great gifts. (Valens General Nature)",
    "JUPITER_TAURUS_NIGHT": "Jupiter indicates childbearing, engendering, desire, loves... prosperity, salaries, great gifts. (Valens General Nature)",
    "JUPITER_GEMINI_DAY": "Jupiter in Gemini [is in] his Detriment. Rules Sagittarius and Pisces [therefore opposes Gemini].",
    "JUPITER_GEMINI_NIGHT": "Jupiter in Gemini [is in] his Detriment. Rules Sagittarius and Pisces [therefore opposes Gemini].",
    "JUPITER_CANCER_DAY": "Jupiter has its exaltation in Cancer. Signifies prosperity, salaries, great gifts, an abundance of crops.",
    "JUPITER_CANCER_NIGHT": "Jupiter has its exaltation in Cancer. Signifies prosperity, salaries, great gifts, an abundance of crops.",
    "JUPITER_LEO_DAY": "Jupiter rules the fiery triplicity by night.",
    "JUPITER_LEO_NIGHT": "Jupiter rules the fiery triplicity by night.",
    "JUPITER_VIRGO_DAY": "Jupiter in Virgo [is in] his Detriment.",
    "JUPITER_VIRGO_NIGHT": "Jupiter in Virgo [is in] his Detriment.",
    "JUPITER_LIBRA_DAY": "Jupiter indicates justice, offices, officeholding, ranks, authority over temples. (Valens General Nature)",
    "JUPITER_LIBRA_NIGHT": "Jupiter indicates justice, offices, officeholding, ranks, authority over temples. (Valens General Nature)",
    "JUPITER_SCORPIO_DAY": "Jupiter indicates justice, offices, officeholding, ranks, authority over temples. (Valens General Nature)",
    "JUPITER_SCORPIO_NIGHT": "Jupiter indicates justice, offices, officeholding, ranks, authority over temples. (Valens General Nature)",
    "JUPITER_SAGITTARIUS_DAY": "Jupiter rules Sagittarius and Pisces. Indicates childbearing, engendering, desire, loves, political ties.",
    "JUPITER_SAGITTARIUS_NIGHT": "Jupiter rules Sagittarius and Pisces. Indicates childbearing, engendering, desire, loves, political ties.",
    "JUPITER_CAPRICORN_DAY": "Jupiter in Capricorn [is in] his Fall. Signifies the tapeinoma [depression/fall].",
    "JUPITER_CAPRICORN_NIGHT": "Jupiter in Capricorn [is in] his Fall. Signifies the tapeinoma [depression/fall].",
    "JUPITER_AQUARIUS_DAY": "Jupiter in Aquarius... [is good if return Venus is in Pisces].",
    "JUPITER_AQUARIUS_NIGHT": "Jupiter in Aquarius... [is good if return Venus is in Pisces].",
    "JUPITER_PISCES_DAY": "Jupiter rules Sagittarius and Pisces. Signifies the exaltation of Venus [by association].",
    "JUPITER_PISCES_NIGHT": "Jupiter rules Sagittarius and Pisces. Signifies the exaltation of Venus [by association].",
    
    # MARS (Found in preview)
    "MARS_ARIES_DAY": "Mars rules Aries. Indicates force, wars, plunderings, screams, violence. Decoration of clothing.",
    "MARS_ARIES_NIGHT": "Mars rules Aries. Indicates force, wars, plunderings, screams, violence. Decoration of clothing."
}

def patch_manual():
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    for k, v in PATCHES.items():
        data[k] = v
        
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    print("Manual Patch Applied.")

if __name__ == "__main__":
    patch_manual()
