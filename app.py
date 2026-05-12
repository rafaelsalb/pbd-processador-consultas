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
    ok_steps = []
    try:
        tree = parser.parse()
        ok_steps.append("Parse")
        semantic_analyzer = SemanticAnalyzer()
        semantic_analyzer.analyze(tree)
        ok_steps.append("Análise Semântica")
        planner = ExecutionPlan()
        plan = planner.build(tree)
        ok_steps.append("Conversão para Álgebra Relacional")
        unoptimized_plan = ExecutionGraph().jsonify(plan)
        optimizer = TreeOptimizer()
        optimized_plan = optimizer.optimize(plan)
        ok_steps.append("Otimização")
        execution_plan = ExecutionGraph().jsonify(optimized_plan)
    except Exception as e:
        return jsonify({"error": str(e), "steps": ok_steps}), 400
    return jsonify({"query": query, "execution_plan": execution_plan, "unoptimized_plan": unoptimized_plan, "steps": ok_steps})

@app.get("/catalog")
def get_catalog():
    schema = Catalog().schema
    for table, columns in schema.items():
        schema[table] = list([f"{table}.{col}" for col in columns])
    print("Schema:", schema)
    return jsonify(schema)


if __name__ == "__main__":
    app.run(debug=True)
