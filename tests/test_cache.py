from src.rag.cache import cache_version, normalize


def test_normalize_ignore_casse_et_accents():
    assert normalize("Quelles sont les compétences de Thomas ?") == (
        "quelles sont les competences de thomas"
    )
    assert normalize("QUELLES   SONT les compétences...") == (
        "quelles sont les competences"
    )


def test_normalize_conserve_les_chiffres():
    assert normalize("Score TOEIC : 985/990") == "score toeic 985 990"


def test_cache_version_est_stable_et_courte():
    version = cache_version()
    assert version == cache_version()
    assert len(version) == 32
    assert version.isalnum()
