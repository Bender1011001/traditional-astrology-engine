
import swisseph as swe
try:
    print("SE_ECL2HOR:", swe.SE_ECL2HOR)
except AttributeError:
    print("SE_ECL2HOR not found")

try:
    print("ECL2HOR:", swe.ECL2HOR)
except AttributeError:
    print("ECL2HOR not found")
