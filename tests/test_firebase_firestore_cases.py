"""
Comprehensive unit tests for firebase_firestore_cases.py module.

This test suite validates the structure, content, and metadata of Firebase Firestore
cases following TDD best practices. Tests ensure the modular case file meets all
specifications for the case-base-modular-refactoring project.

Test Coverage:
- File existence and import validation
- FIREBASE_FIRESTORE_CASES variable structure
- Case count validation (exactly 4 cases)
- Required field presence for all cases
- Field type validation
- Field content validation (non-empty, correct values)
- Firestore CRUD operations coverage
- Tag keyword validation
- Individual case structure validation
- Tag content quality validation
"""

import pytest
from pathlib import Path
from typing import Any, Dict, List


# Test Group 1: File and Module Structure
class TestFileAndModuleStructure:
    """Test suite for validating file existence and module import."""

    def test_firebase_firestore_cases_file_exists(self):
        """Verify that cases/firebase/firebase_firestore_cases.py file exists."""
        file_path = Path('cases/firebase/firebase_firestore_cases.py')
        assert file_path.exists(), f'Expected file not found: {file_path}'
        assert file_path.is_file(), f'Expected path to be a file: {file_path}'
        assert file_path.suffix == '.py', f'Expected .py extension: {file_path}'

    def test_firebase_firestore_cases_module_importable(self):
        """Verify that firebase_firestore_cases module can be imported without errors."""
        try:
            from cases.firebase import firebase_firestore_cases
            assert firebase_firestore_cases is not None
        except ImportError as e:
            pytest.fail(f'Failed to import firebase_firestore_cases module: {e}')


# Test Group 2: FIREBASE_FIRESTORE_CASES Variable Structure
class TestFirebaseFirestoreCasesVariable:
    """Test suite for validating FIREBASE_FIRESTORE_CASES variable structure."""

    def test_firebase_firestore_cases_variable_exists(self):
        """Verify that FIREBASE_FIRESTORE_CASES variable exists in the module."""
        from cases.firebase import firebase_firestore_cases
        assert hasattr(firebase_firestore_cases, 'FIREBASE_FIRESTORE_CASES'), \
            'Module must define FIREBASE_FIRESTORE_CASES variable'

    def test_firebase_firestore_cases_is_list(self):
        """Verify that FIREBASE_FIRESTORE_CASES is a list."""
        from cases.firebase.firebase_firestore_cases import FIREBASE_FIRESTORE_CASES
        assert isinstance(FIREBASE_FIRESTORE_CASES, list), \
            f'FIREBASE_FIRESTORE_CASES must be a list, got {type(FIREBASE_FIRESTORE_CASES)}'


# Test Group 3: Case Count Validation
class TestCaseCount:
    """Test suite for validating the number of Firebase Firestore cases."""

    def test_firebase_firestore_cases_count(self):
        """Verify that FIREBASE_FIRESTORE_CASES contains exactly 5 cases."""
        from cases.firebase.firebase_firestore_cases import FIREBASE_FIRESTORE_CASES
        assert len(FIREBASE_FIRESTORE_CASES) == 5, \
            f'Expected exactly 5 cases, got {len(FIREBASE_FIRESTORE_CASES)}'


# Test Group 4: Required Fields Presence
class TestRequiredFieldsPresence:
    """Test suite for validating presence of all required fields in every case."""

    @pytest.fixture
    def cases(self) -> List[Dict[str, Any]]:
        """Fixture providing FIREBASE_FIRESTORE_CASES for tests."""
        from cases.firebase.firebase_firestore_cases import FIREBASE_FIRESTORE_CASES
        return FIREBASE_FIRESTORE_CASES

    def test_all_cases_have_problem_field(self, cases: List[Dict[str, Any]]):
        """Verify that all cases have a 'problem' field."""
        for idx, case in enumerate(cases):
            assert 'problem' in case, \
                f'Case {idx} missing required field: problem'

    def test_all_cases_have_solution_field(self, cases: List[Dict[str, Any]]):
        """Verify that all cases have a 'solution' field."""
        for idx, case in enumerate(cases):
            assert 'solution' in case, \
                f'Case {idx} missing required field: solution'

    def test_all_cases_have_category_field(self, cases: List[Dict[str, Any]]):
        """Verify that all cases have a 'category' field."""
        for idx, case in enumerate(cases):
            assert 'category' in case, \
                f'Case {idx} missing required field: category'

    def test_all_cases_have_subcategory_field(self, cases: List[Dict[str, Any]]):
        """Verify that all cases have a 'subcategory' field."""
        for idx, case in enumerate(cases):
            assert 'subcategory' in case, \
                f'Case {idx} missing required field: subcategory'

    def test_all_cases_have_tags_field(self, cases: List[Dict[str, Any]]):
        """Verify that all cases have a 'tags' field."""
        for idx, case in enumerate(cases):
            assert 'tags' in case, \
                f'Case {idx} missing required field: tags'


# Test Group 5: Field Type Validation
class TestFieldTypes:
    """Test suite for validating data types of all fields."""

    @pytest.fixture
    def cases(self) -> List[Dict[str, Any]]:
        """Fixture providing FIREBASE_FIRESTORE_CASES for tests."""
        from cases.firebase.firebase_firestore_cases import FIREBASE_FIRESTORE_CASES
        return FIREBASE_FIRESTORE_CASES

    def test_problem_fields_are_strings(self, cases: List[Dict[str, Any]]):
        """Verify that all 'problem' fields are strings."""
        for idx, case in enumerate(cases):
            assert isinstance(case.get('problem'), str), \
                f'Case {idx} problem field must be str, got {type(case.get("problem"))}'

    def test_solution_fields_are_strings(self, cases: List[Dict[str, Any]]):
        """Verify that all 'solution' fields are strings."""
        for idx, case in enumerate(cases):
            assert isinstance(case.get('solution'), str), \
                f'Case {idx} solution field must be str, got {type(case.get("solution"))}'

    def test_category_fields_are_strings(self, cases: List[Dict[str, Any]]):
        """Verify that all 'category' fields are strings."""
        for idx, case in enumerate(cases):
            assert isinstance(case.get('category'), str), \
                f'Case {idx} category field must be str, got {type(case.get("category"))}'

    def test_subcategory_fields_are_strings(self, cases: List[Dict[str, Any]]):
        """Verify that all 'subcategory' fields are strings."""
        for idx, case in enumerate(cases):
            assert isinstance(case.get('subcategory'), str), \
                f'Case {idx} subcategory field must be str, got {type(case.get("subcategory"))}'

    def test_tags_fields_are_lists(self, cases: List[Dict[str, Any]]):
        """Verify that all 'tags' fields are lists."""
        for idx, case in enumerate(cases):
            assert isinstance(case.get('tags'), list), \
                f'Case {idx} tags field must be list, got {type(case.get("tags"))}'


# Test Group 6: Field Content Validation
class TestFieldContent:
    """Test suite for validating content and values of all fields."""

    @pytest.fixture
    def cases(self) -> List[Dict[str, Any]]:
        """Fixture providing FIREBASE_FIRESTORE_CASES for tests."""
        from cases.firebase.firebase_firestore_cases import FIREBASE_FIRESTORE_CASES
        return FIREBASE_FIRESTORE_CASES

    def test_problem_fields_non_empty(self, cases: List[Dict[str, Any]]):
        """Verify that all 'problem' fields are non-empty strings."""
        for idx, case in enumerate(cases):
            problem = case.get('problem', '')
            assert len(problem) > 0, \
                f'Case {idx} problem field must not be empty'
            assert problem.strip() != '', \
                f'Case {idx} problem field must not be only whitespace'

    def test_solution_fields_non_empty(self, cases: List[Dict[str, Any]]):
        """Verify that all 'solution' fields are non-empty strings."""
        for idx, case in enumerate(cases):
            solution = case.get('solution', '')
            assert len(solution) > 0, \
                f'Case {idx} solution field must not be empty'
            assert solution.strip() != '', \
                f'Case {idx} solution field must not be only whitespace'

    def test_category_equals_firebase(self, cases: List[Dict[str, Any]]):
        """Verify that all cases have category='firebase'."""
        for idx, case in enumerate(cases):
            assert case.get('category') == 'firebase', \
                f'Case {idx} category must be "firebase", got "{case.get("category")}"'

    def test_subcategory_equals_firestore(self, cases: List[Dict[str, Any]]):
        """Verify that all cases have subcategory='firestore'."""
        for idx, case in enumerate(cases):
            assert case.get('subcategory') == 'firestore', \
                f'Case {idx} subcategory must be "firestore", got "{case.get("subcategory")}"'

    def test_tags_non_empty_lists(self, cases: List[Dict[str, Any]]):
        """Verify that all 'tags' fields are non-empty lists."""
        for idx, case in enumerate(cases):
            tags = case.get('tags', [])
            assert len(tags) > 0, \
                f'Case {idx} tags list must not be empty'

    def test_all_tags_are_strings(self, cases: List[Dict[str, Any]]):
        """Verify that all elements in 'tags' lists are strings."""
        for case_idx, case in enumerate(cases):
            tags = case.get('tags', [])
            for tag_idx, tag in enumerate(tags):
                assert isinstance(tag, str), \
                    f'Case {case_idx} tag {tag_idx} must be str, got {type(tag)}'


# Test Group 7: Firestore CRUD Operations Coverage
class TestFirestoreCRUDCoverage:
    """Test suite for validating coverage of Firestore CRUD operations."""

    @pytest.fixture
    def cases(self) -> List[Dict[str, Any]]:
        """Fixture providing FIREBASE_FIRESTORE_CASES for tests."""
        from cases.firebase.firebase_firestore_cases import FIREBASE_FIRESTORE_CASES
        return FIREBASE_FIRESTORE_CASES

    def _search_in_case(self, case: Dict[str, Any], keywords: List[str]) -> bool:
        """
        Helper method to search for keywords in case problem and solution fields.

        Args:
            case: The case dictionary to search
            keywords: List of keywords to search for (case-insensitive)

        Returns:
            True if any keyword is found in problem or solution, False otherwise
        """
        problem_lower = case.get('problem', '').lower()
        solution_lower = case.get('solution', '').lower()
        tags_lower = [tag.lower() for tag in case.get('tags', [])]

        for keyword in keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in problem_lower or keyword_lower in solution_lower:
                return True
            if any(keyword_lower in tag for tag in tags_lower):
                return True

        return False

    def test_create_operation_covered(self, cases: List[Dict[str, Any]]):
        """Verify that CREATE operations are covered in at least one case."""
        keywords = ['add', 'create', 'set', 'document', 'insert', 'write', 'new']
        found = any(self._search_in_case(case, keywords) for case in cases)
        assert found, \
            f'No case found covering CREATE operations. Keywords: {keywords}'

    def test_read_operation_covered(self, cases: List[Dict[str, Any]]):
        """Verify that READ operations are covered in at least one case."""
        keywords = ['get', 'read', 'query', 'fetch', 'retrieve', 'find', 'search', 'list']
        found = any(self._search_in_case(case, keywords) for case in cases)
        assert found, \
            f'No case found covering READ operations. Keywords: {keywords}'

    def test_update_operation_covered(self, cases: List[Dict[str, Any]]):
        """Verify that UPDATE operations are covered in at least one case."""
        keywords = ['update', 'modify', 'edit', 'change', 'patch', 'merge']
        found = any(self._search_in_case(case, keywords) for case in cases)
        assert found, \
            f'No case found covering UPDATE operations. Keywords: {keywords}'

    def test_delete_operation_covered(self, cases: List[Dict[str, Any]]):
        """Verify that DELETE operations are covered in at least one case."""
        keywords = ['delete', 'remove', 'destroy', 'clear']
        found = any(self._search_in_case(case, keywords) for case in cases)
        assert found, \
            f'No case found covering DELETE operations. Keywords: {keywords}'


# Test Group 8: Firestore-Specific Keywords Validation
class TestFirestoreKeywords:
    """Test suite for validating presence of Firestore-specific keywords in tags."""

    @pytest.fixture
    def cases(self) -> List[Dict[str, Any]]:
        """Fixture providing FIREBASE_FIRESTORE_CASES for tests."""
        from cases.firebase.firebase_firestore_cases import FIREBASE_FIRESTORE_CASES
        return FIREBASE_FIRESTORE_CASES

    def test_tags_contain_firestore_keywords(self, cases: List[Dict[str, Any]]):
        """Verify that tags across all cases contain Firestore-related keywords."""
        firestore_keywords = [
            'firestore', 'database', 'collection', 'document', 'nosql',
            'firebase', 'query', 'data', 'crud', 'cloud', 'realtime',
            'snapshot', 'reference', 'field', 'subcollection'
        ]

        all_tags_lower = []
        for case in cases:
            all_tags_lower.extend([tag.lower() for tag in case.get('tags', [])])

        found_keywords = []
        for keyword in firestore_keywords:
            if any(keyword in tag for tag in all_tags_lower):
                found_keywords.append(keyword)

        assert len(found_keywords) > 0, \
            f'Tags must contain Firestore keywords. Expected any of: {firestore_keywords}'


# Test Group 9: Individual Case Structure Validation
class TestIndividualCaseStructure:
    """Test suite for detailed validation of each individual case."""

    @pytest.fixture
    def cases(self) -> List[Dict[str, Any]]:
        """Fixture providing FIREBASE_FIRESTORE_CASES for tests."""
        from cases.firebase.firebase_firestore_cases import FIREBASE_FIRESTORE_CASES
        return FIREBASE_FIRESTORE_CASES

    def test_case_0_structure(self, cases: List[Dict[str, Any]]):
        """Verify that case 0 has all required fields with valid content."""
        case = cases[0]
        assert 'problem' in case and isinstance(case['problem'], str) and len(case['problem']) > 0
        assert 'solution' in case and isinstance(case['solution'], str) and len(case['solution']) > 0
        assert 'category' in case and case['category'] == 'firebase'
        assert 'subcategory' in case and case['subcategory'] == 'firestore'
        assert 'tags' in case and isinstance(case['tags'], list) and len(case['tags']) > 0

    def test_case_1_structure(self, cases: List[Dict[str, Any]]):
        """Verify that case 1 has all required fields with valid content."""
        case = cases[1]
        assert 'problem' in case and isinstance(case['problem'], str) and len(case['problem']) > 0
        assert 'solution' in case and isinstance(case['solution'], str) and len(case['solution']) > 0
        assert 'category' in case and case['category'] == 'firebase'
        assert 'subcategory' in case and case['subcategory'] == 'firestore'
        assert 'tags' in case and isinstance(case['tags'], list) and len(case['tags']) > 0

    def test_case_2_structure(self, cases: List[Dict[str, Any]]):
        """Verify that case 2 has all required fields with valid content."""
        case = cases[2]
        assert 'problem' in case and isinstance(case['problem'], str) and len(case['problem']) > 0
        assert 'solution' in case and isinstance(case['solution'], str) and len(case['solution']) > 0
        assert 'category' in case and case['category'] == 'firebase'
        assert 'subcategory' in case and case['subcategory'] == 'firestore'
        assert 'tags' in case and isinstance(case['tags'], list) and len(case['tags']) > 0

    def test_case_3_structure(self, cases: List[Dict[str, Any]]):
        """Verify that case 3 has all required fields with valid content."""
        case = cases[3]
        assert 'problem' in case and isinstance(case['problem'], str) and len(case['problem']) > 0
        assert 'solution' in case and isinstance(case['solution'], str) and len(case['solution']) > 0
        assert 'category' in case and case['category'] == 'firebase'
        assert 'subcategory' in case and case['subcategory'] == 'firestore'
        assert 'tags' in case and isinstance(case['tags'], list) and len(case['tags']) > 0


# Test Group 10: Tag Content Quality
class TestTagContentQuality:
    """Test suite for validating quality and consistency of tags."""

    @pytest.fixture
    def cases(self) -> List[Dict[str, Any]]:
        """Fixture providing FIREBASE_FIRESTORE_CASES for tests."""
        from cases.firebase.firebase_firestore_cases import FIREBASE_FIRESTORE_CASES
        return FIREBASE_FIRESTORE_CASES

    def test_tags_no_empty_strings(self, cases: List[Dict[str, Any]]):
        """Verify that no tags are empty strings."""
        for case_idx, case in enumerate(cases):
            tags = case.get('tags', [])
            for tag_idx, tag in enumerate(tags):
                assert tag.strip() != '', \
                    f'Case {case_idx} tag {tag_idx} must not be empty or whitespace-only'

    def test_tags_no_duplicates_within_case(self, cases: List[Dict[str, Any]]):
        """Verify that individual cases have no duplicate tags."""
        for case_idx, case in enumerate(cases):
            tags = case.get('tags', [])
            unique_tags = set(tags)
            assert len(tags) == len(unique_tags), \
                f'Case {case_idx} has duplicate tags: {[t for t in tags if tags.count(t) > 1]}'

    def test_tags_are_lowercase(self, cases: List[Dict[str, Any]]):
        """Verify that tags follow lowercase convention."""
        for case_idx, case in enumerate(cases):
            tags = case.get('tags', [])
            for tag_idx, tag in enumerate(tags):
                assert tag == tag.lower(), \
                    f'Case {case_idx} tag {tag_idx} should be lowercase: "{tag}" -> "{tag.lower()}"'
