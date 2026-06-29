

import logging
from langchain_core.tools import tool
from database import ORDERS, PRODUCTS

logger = logging.getLogger(__name__)


@tool
def get_order(order_id: str) -> dict:
    """
    Fetch complete order details for a customer using their order ID.
    Use this when the customer asks about order status, shipping,
    delivery ETA, or any question that includes an order ID like ORD-1002.
    """
    logger.info(f"[TOOL CALLED] get_order | order_id={order_id}")

    order_id = order_id.strip().upper()

    if not order_id:
        result = {"error": "Order ID cannot be empty. Please provide a valid order ID."}
        logger.warning("[TOOL RESULT] get_order | Empty order_id")
        return result

    if order_id not in ORDERS:
        result = {"error": f"Order '{order_id}' not found. Please check your order ID and try again."}
        logger.warning(f"[TOOL RESULT] get_order | Not found: {order_id}")
        return result

    result = ORDERS[order_id]
    logger.info(f"[TOOL RESULT] get_order | Found: {result['item']}")
    return result


@tool
def search_products(query: str) -> list | dict:
    """
    Search the product catalog using a keyword or phrase.
    Use this when the customer wants to find products, browse options,
    or look for alternatives. Examples: 'shoes', 'cheap headphones',
    'running shoes under 5000'. Returns products sorted by price ascending.
    """
    logger.info(f"[TOOL CALLED] search_products | query={query}")

    if not query or not query.strip():
        result = {"error": "Search query cannot be empty."}
        logger.warning("[TOOL RESULT] search_products | Empty query")
        return result

    query_lower = query.strip().lower()

    matches = [
        product for product in PRODUCTS.values()
        if query_lower in product["name"].lower()
        or query_lower in product["category"].lower()
        or query_lower in product["description"].lower()
    ]

    if not matches:
        result = {"error": f"No products found for '{query}'. Try keywords like 'shoes', 'belt', or 'headphones'."}
        logger.warning(f"[TOOL RESULT] search_products | No results: {query}")
        return result

    matches = sorted(matches, key=lambda x: x["price"])
    logger.info(f"[TOOL RESULT] search_products | {len(matches)} results for: {query}")
    return matches


@tool
def get_product(product_id: str) -> dict:
    """
    Fetch detailed information about a specific product using its product ID.
    Use this when you already have a product_id from an order or search result
    and need full details like price, stock status, rating, and description.
    """
    logger.info(f"[TOOL CALLED] get_product | product_id={product_id}")

    product_id = product_id.strip().upper()

    if not product_id:
        result = {"error": "Product ID cannot be empty."}
        logger.warning("[TOOL RESULT] get_product | Empty product_id")
        return result

    if product_id not in PRODUCTS:
        result = {"error": f"Product '{product_id}' not found."}
        logger.warning(f"[TOOL RESULT] get_product | Not found: {product_id}")
        return result

    result = PRODUCTS[product_id]
    logger.info(f"[TOOL RESULT] get_product | Found: {result['name']}")
    return result


# List of all tools — passed to the LLM and ToolNode
TOOLS = [get_order, search_products, get_product]
