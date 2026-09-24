import sys
from pathlib import Path

src_dir = Path(__file__).resolve().parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# import ..src.masks as masks
import masks

number_card = "7000792289606361"
bank_account = "73654108430135874305"

result = masks.get_mask_card_number(number_card)
result2 = masks.get_mask_account(bank_account)

print(result)
print(result2)