from flask import Flask, request, jsonify, render_template

from execution_graph import ExecutionGraph
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
        execution_plan = ExecutionGraph().jsonify(plan)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"query": query, "execution_plan": execution_plan})


if __name__ == "__main__":
    app.run(debug=True)
