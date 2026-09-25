import sys
from pathlib import Path

src_dir = Path(__file__).resolve().parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# import ..src.masks as masks
import widget


test_list = ["Maestro 1596837868705199",
    "Счет 64686473678894779589",
    "MasterCard 7158300734726758",
    "Счет 35383033474447895560",
    "Visa Classic 6831982476737658",
    "Visa Platinum 8990922113665229",
    "Visa Gold 5999414228426353",
    "Счет 73654108430135874305"]

#print(widget.mask_account_card("abc123"))
#print(widget.mask_account_card(test_list[4]))
#print(test_list[1])

for test_element in test_list:
    print(widget.mask_account_card(test_element))
