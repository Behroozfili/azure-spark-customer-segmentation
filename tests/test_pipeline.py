
import sys
sys.path.append("src")  

def test_pipeline_runs_without_crashing():
    try:
        import main 
    except Exception as e:
        assert False, f"Pipeline crashed with error: {e}"
