from .model import Stock
from .repository import get_stocks


def get_stock_name(stock_code: str) -> str | None:
    """Get the stock name for a stock code.

    Args:
        stock_code (str): the stock code to get the name for.
    Returns:
        str | None: the name of the stock, or None if the stock code is invalid.
    """
    stock_info = get_stocks([stock_code]).get(stock_code)
    if stock_info is None:
        return None
    else:
        return stock_info.name


def get_stock_infos(stock_codes: list[str]) -> dict[str, Stock | None]:
    """Get the information about a list of stock code.

    Args:
        stock_codes (list[str]): the stock codes to search by

    Returns:
        dict[str, Stock | None]: dictionary mapping stock codes to their information, None if invalid code is given.
    """
    return get_stocks(stock_codes)
