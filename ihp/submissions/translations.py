def get_translation(language):
    if language.language == "French":
        import translations_fr
        return translations_fr
    elif language.language == "Spanish":
        import translations_es
        return translations_es        
    else:
        import translations_en
        return translations_en

