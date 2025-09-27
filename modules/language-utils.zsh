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
        # German dialects inherit from German
        de-*)
            base_lang="de"
            dialect_suffix="${selected_lang#de-}"
            ;;
        # Spanish variants inherit from Spanish
        es-*)
            base_lang="es"
            dialect_suffix="${selected_lang#es-}"
            ;;
        # Independent languages (no inheritance)
        en|de|es|fr|it|zh|hi|eu|ca|gl)
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

    # Override with dialect-specific translations if available
    if [[ -n "$dialect_suffix" ]]; then
        local DIALECT_LANG_FILE="$SCRIPT_DIR/lang/${selected_lang}.conf"
        if [[ -f "$DIALECT_LANG_FILE" ]]; then
            source "$DIALECT_LANG_FILE"
        fi
    fi
}

# Get language display name with proper categorization
get_language_display_name() {
    local lang_code="$1"

    case "$lang_code" in
        # Independent languages
        en) echo "🇬🇧 English" ;;
        de) echo "🇩🇪 Deutsch" ;;
        es) echo "🇪🇸 Español" ;;
        fr) echo "🇫🇷 Français" ;;
        it) echo "🇮🇹 Italiano" ;;
        zh) echo "🇨🇳 中文 (Mandarin)" ;;
        hi) echo "🇮🇳 हिन्दी (Hindi)" ;;

        # Independent regional languages (not dialects!)
        eu) echo "🏴 Euskera (Basque)" ;;
        ca) echo "🏴 Català (Catalan)" ;;
        gl) echo "🏴 Galego (Galician)" ;;

        # German dialects
        de-schwaebisch) echo "🇩🇪 Schwäbisch (German dialect)" ;;
        de-bayerisch) echo "🇩🇪 Bayerisch (German dialect)" ;;
        de-saechsisch) echo "🇩🇪 Sächsisch (German dialect)" ;;

        # Spanish regional variants
        es-mexicano) echo "🇲🇽 Español Mexicano" ;;
        es-argentino) echo "🇦🇷 Español Argentino" ;;
        es-colombiano) echo "🇨🇴 Español Colombiano" ;;
        es-venezolano) echo "🇻🇪 Español Venezolano" ;;
        es-chileno) echo "🇨🇱 Español Chileno" ;;
        es-andaluz) echo "🇪🇸 Andaluz (Spanish dialect)" ;;

        *) echo "$lang_code" ;;
    esac
}

# Check if language is a dialect
is_dialect() {
    local lang_code="$1"

    case "$lang_code" in
        de-*|es-*)
            return 0  # Is a dialect
            ;;
        *)
            return 1  # Is an independent language
            ;;
    esac
}

# Get base language for a dialect
get_base_language() {
    local lang_code="$1"

    case "$lang_code" in
        de-*) echo "de" ;;
        es-*) echo "es" ;;
        *) echo "$lang_code" ;;  # Already a base language
    esac
}