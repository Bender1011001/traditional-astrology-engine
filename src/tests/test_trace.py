from src.engine.trace import CAT_ASTRONOMY, ComputationTrace


def test_computation_trace_initialization():
    trace = ComputationTrace(
        subject_name="John Doe", birth_data="2000-01-01 12:00, New York"
    )
    assert trace.subject_name == "John Doe"
    assert trace.birth_data == "2000-01-01 12:00, New York"
    assert len(trace.steps) == 0
    assert trace.elapsed_ms >= 0


def test_computation_trace_add():
    trace = ComputationTrace()
    step = trace.add(
        category=CAT_ASTRONOMY,
        technique="Calculation",
        inputs={"param": 1},
        rule="Some Rule",
        source="Author",
        calculation="1+1=2",
        result=2,
        notes="note",
        subsection="sub",
    )

    assert len(trace.steps) == 1
    assert step == trace.steps[0]
    assert step.step_number == 1
    assert step.category == CAT_ASTRONOMY
    assert step.technique == "Calculation"
    assert step.inputs == {"param": 1}
    assert step.rule == "Some Rule"
    assert step.source == "Author"
    assert step.calculation == "1+1=2"
    assert step.result == 2
    assert step.notes == "note"
    assert step.subsection == "sub"


def test_computation_trace_categories_and_selection():
    trace = ComputationTrace()
    trace.add(
        category="Cat A",
        technique="T1",
        inputs={},
        rule="-",
        source="-",
        calculation="-",
        result="R",
    )
    trace.add(
        category="Cat A",
        technique="T2",
        inputs={},
        rule="-",
        source="-",
        calculation="-",
        result="R",
    )
    trace.add(
        category="Cat B",
        technique="T3",
        inputs={},
        rule="-",
        source="-",
        calculation="-",
        result="R",
    )

    assert trace.categories == ["Cat A", "Cat B"]

    cat_a_steps = trace.steps_by_category("Cat A")
    assert len(cat_a_steps) == 2
    assert cat_a_steps[0].technique == "T1"


def test_computation_trace_to_dict():
    trace = ComputationTrace(subject_name="Alice", birth_data="TestData")
    trace.add(
        category="Cat A",
        technique="T1",
        inputs={"a": "b"},
        rule="Rule",
        source="Src",
        calculation="Calc",
        result="Result",
        notes="Note",
    )

    d = trace.to_dict()
    assert d["subject_name"] == "Alice"
    assert d["birth_data"] == "TestData"
    assert "generated_at" in d
    assert d["total_steps"] == 1
    assert "elapsed_ms" in d
    assert d["categories"] == ["Cat A"]

    step_dict = d["steps"][0]
    assert step_dict["step"] == 1
    assert step_dict["category"] == "Cat A"
    assert step_dict["technique"] == "T1"
    assert step_dict["inputs"] == {"a": "b"}
    assert step_dict["rule"] == "Rule"
    assert step_dict["source"] == "Src"
    assert step_dict["calculation"] == "Calc"
    assert step_dict["result"] == "Result"
    assert step_dict["notes"] == "Note"
