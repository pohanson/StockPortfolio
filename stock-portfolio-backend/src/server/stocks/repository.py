from .model import Stock
from .stock_code_name_dict import stock_code_name_dict


def get_stock(stock_code) -> Stock | None:
    """Get the stock information for a stock code.

    Args:
        stock_code (str): the stock code to search by
    Returns:
        Stock | None: the stock object, None if invalid code is given.
    """
    name = stock_code_name_dict.get(stock_code)
    return Stock(code=stock_code, name=name) if name else None


def get_stocks(stock_codes: list[str]) -> dict[str, Stock | None]:
    """Get the information about a list of stock code.

    Args:
        stock_codes (list[str]): the stock codes to search by

    Returns:
        list[dict]: list of stock information, None if invalid code is given.
    """
    return {stock_code: get_stock(stock_code) for stock_code in stock_codes}


def get_all_stock_codes() -> list[str]:
    """Get all the stock codes.

    Returns:
        list[str]: list of all stock codes.
    """
    return list(stock_code_name_dict.keys())
