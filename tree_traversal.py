def breadth_first_traversal(node):
    print(f"Visiting node: {node}\n")
    if node is None:
        print("Node is None, returning.")
        return
    yield node
    if hasattr(node, "child"):
        yield from breadth_first_traversal(node.child)
    if hasattr(node, "left_node"):
        yield from breadth_first_traversal(node.left_node)
    if hasattr(node, "right_node"):
        yield from breadth_first_traversal(node.right_node)
