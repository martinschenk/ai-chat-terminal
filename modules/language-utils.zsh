#!/bin/zsh
# Language Inheritance System
# Handles proper language vs dialect classification

# Load language with inheritance support
load_language_with_inheritance() {
    local selected_lang="$1"
    local base_lang=""
    local dialect_suffix=""

    # Determine if this is a dialect and what the base language is
    case "$selected_lang" in
        # Supported languages
        en|de|es)
            base_lang="$selected_lang"
            ;;
        *)
            # Fallback to English
            base_lang="en"
            ;;
    esac

    # Load base language first
    local BASE_LANG_FILE="$SCRIPT_DIR/lang/${base_lang}.conf"
    if [[ -f "$BASE_LANG_FILE" ]]; then
        source "$BASE_LANG_FILE"
    fi

}

# Get language display name with proper categorization
get_language_display_name() {
    local lang_code="$1"

    case "$lang_code" in
        # Supported languages
        en) echo "🇬🇧 English" ;;
        de) echo "🇩🇪 Deutsch" ;;
        es) echo "🇪🇸 Español" ;;

        *) echo "$lang_code" ;;
    esac
}

# Check if language is a dialect
is_dialect() {
    # No dialects supported anymore
    return 1
}

# Get base language for a dialect
get_base_language() {
    local lang_code="$1"
    # Return the language code as-is (no dialects)
    echo "$lang_code"
}