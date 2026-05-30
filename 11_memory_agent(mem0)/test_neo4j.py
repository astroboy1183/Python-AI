"""
Test Neo4j Aura connection by performing real CRUD operations.

Steps:
1. Verify connection
2. Show what's already in the database (node + relationship counts)
3. Create a test node with properties
4. Query it back
5. Create a relationship between two nodes
6. Query that relationship
7. Clean up the test data
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")

print(f"Connecting to: {URI}\n")

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
driver.verify_connectivity()
print("✓ Connection verified\n")

with driver.session() as session:
    # ── 1. Database snapshot ──────────────────────────────────────────────────
    print("── Current database snapshot ──")
    node_count = session.run("MATCH (n) RETURN count(n) AS c").single()["c"]
    rel_count = session.run("MATCH ()-[r]->() RETURN count(r) AS c").single()["c"]
    print(f"  Total nodes:         {node_count}")
    print(f"  Total relationships: {rel_count}")

    if node_count > 0:
        print("\n  Sample nodes (first 5):")
        for record in session.run("MATCH (n) RETURN n, labels(n) AS labels LIMIT 5"):
            labels = record["labels"]
            props = dict(record["n"])
            print(f"    • {labels} {props}")
    print()

    # ── 2. CREATE a test node ─────────────────────────────────────────────────
    print("── Creating a test node ──")
    session.run("""
        CREATE (p:TestPerson {name: $name, role: $role, created: datetime()})
    """, name="Jayanth", role="developer")
    print("  ✓ Created (:TestPerson {name: 'Jayanth', role: 'developer'})\n")

    # ── 3. READ it back ───────────────────────────────────────────────────────
    print("── Reading it back ──")
    result = session.run("""
        MATCH (p:TestPerson {name: $name})
        RETURN p.name AS name, p.role AS role, p.created AS created
    """, name="Jayanth").single()
    print(f"  ✓ Found: name={result['name']}, role={result['role']}, created={result['created']}\n")

    # ── 4. CREATE a relationship ──────────────────────────────────────────────
    print("── Creating a related node + relationship ──")
    session.run("""
        MATCH (p:TestPerson {name: $name})
        CREATE (c:TestConcept {name: 'LangGraph'})
        CREATE (p)-[r:LEARNED {on: datetime()}]->(c)
    """, name="Jayanth")
    print("  ✓ Created (:TestPerson)-[:LEARNED]->(:TestConcept {name: 'LangGraph'})\n")

    # ── 5. QUERY the relationship ─────────────────────────────────────────────
    print("── Querying the relationship ──")
    rel = session.run("""
        MATCH (p:TestPerson {name: $name})-[r:LEARNED]->(c:TestConcept)
        RETURN p.name AS person, type(r) AS rel, c.name AS concept
    """, name="Jayanth").single()
    print(f"  ✓ {rel['person']} -[{rel['rel']}]-> {rel['concept']}\n")

    # ── 6. Clean up ───────────────────────────────────────────────────────────
    print("── Cleaning up test data ──")
    deleted = session.run("""
        MATCH (n)
        WHERE n:TestPerson OR n:TestConcept
        DETACH DELETE n
        RETURN count(n) AS removed
    """).single()["removed"]
    print(f"  ✓ Removed {deleted} test nodes (and their relationships)\n")

driver.close()
print("✓ All read/write operations succeeded — Neo4j is fully functional.")
