from flask import Flask, request, jsonify, render_template

from catalog import Catalog
from execution_graph import ExecutionGraph
from optimizer import TreeOptimizer
from parser import Parser
from relational import ExecutionPlan
from semantic_analyzer import SemanticAnalyzer


app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.post("/execute")
def execute_query():
    data = request.get_json()
    query = data.get("query")
    parser = Parser(query)
    try:
        tree = parser.parse()
        semantic_analyzer = SemanticAnalyzer()
        semantic_analyzer.analyze(tree)
        planner = ExecutionPlan()
        plan = planner.build(tree)
        unoptimized_plan = ExecutionGraph().jsonify(plan)
        optimizer = TreeOptimizer()
        optimized_plan = optimizer.optimize(plan)
        execution_plan = ExecutionGraph().jsonify(optimized_plan)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"query": query, "execution_plan": execution_plan, "unoptimized_plan": unoptimized_plan})

@app.get("/catalog")
def get_catalog():
    schema = Catalog().schema
    for table, columns in schema.items():
        schema[table] = list([f"{table}.{col}" for col in columns])
    print("Schema:", schema)
    return jsonify(schema)


if __name__ == "__main__":
    app.run(debug=True)
