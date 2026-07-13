from app.agents.guardrails import evaluate_brief_guardrails


def make_brief(**overrides):
    brief = {
        "business_name": "Northwind Coffee",
        "one_liner": "A neighborhood coffee shop with slow-brewed espresso.",
        "target_audience": "Young professionals in the city",
        "core_message": "Fresh coffee and a cozy atmosphere",
        "call_to_action": "Visit the cafe this week",
        "palette": {
            "primary": "#7C2D12",
            "secondary": "#F59E0B",
            "accent": "#E7E5E4",
            "neutral": "#FFFFFF",
        },
        "visual": {
            "aesthetic": "warm and inviting",
            "photography_style": "cinematic lifestyle photography",
            "mood": ["cozy", "authentic", "welcoming"],
            "do_not": [],
        },
        "audio": {
            "music_genre": "warm acoustic guitar, relaxed cafe ambiance",
            "voiceover_tone": "friendly and conversational",
            "voice_name": "Kore",
        },
        "voiceover_script": "Stop by for a fresh cup and a calm moment.",
    }
    brief.update(overrides)
    return brief


def test_bias_checker_blocks_discriminatory_language():
    brief = make_brief(core_message="Target only wealthy white men who are old and conservative")

    report = evaluate_brief_guardrails(brief)

    assert report.blocked is True
    assert any(issue["category"] == "bias" for issue in report.issues)


def test_guardrails_allow_inclusive_brief():
    brief = make_brief()

    report = evaluate_brief_guardrails(brief)

    assert report.blocked is False
    assert report.issues == []
