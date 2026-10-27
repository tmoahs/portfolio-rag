from src.rag.generation import _is_refusal


def test_detecte_un_refus_hors_perimetre():
    assert _is_refusal(
        "Je suis un assistant dédié au profil professionnel de Thomas Patout. "
        "Je ne peux donc répondre qu'aux questions portant sur son parcours."
    )


def test_detecte_un_refus_information_absente():
    assert _is_refusal(
        "Je ne dispose pas de cette information dans le profil de Thomas Patout."
    )


def test_ne_detecte_pas_une_reponse_normale():
    assert not _is_refusal(
        "Thomas maîtrise Python et SQL, ainsi que le Machine Learning supervisé."
    )
