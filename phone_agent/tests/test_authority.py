from program.authority import Authority, CommandEnvelope, Decision, decide

def test_external_never_has_authority():
    assert decide(CommandEnvelope("inspect", Authority.EXTERNAL)) is Decision.BLOCK

def test_development_requires_explicit_authorization():
    assert decide(CommandEnvelope("fix the app", Authority.HUMAN, False)) is Decision.REQUIRE_HUMAN_AUTHORIZATION
    assert decide(CommandEnvelope("fix the app", Authority.HUMAN, True)) is Decision.ALLOW

def test_scientific_contract_mutation_is_blocked():
    assert decide(CommandEnvelope("change hypothesis", Authority.HUMAN, True)) is Decision.BLOCK
