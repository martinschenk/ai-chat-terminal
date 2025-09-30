#!/bin/zsh
# Test dash character input in raw mode

echo "Testing dash character in raw terminal mode..."
echo "Type some text with dashes (e.g., 'hello-world'), then press ENTER:"
echo ""

# Save current terminal settings
OLD_STTY=$(stty -g)
stty raw -echo min 1 time 0 2>/dev/null

INPUT=""
while true; do
    char=$(dd bs=1 count=1 2>/dev/null)

    # Get ASCII code for debugging
    ascii=$(printf '%d' "'$char")

    if [[ $char == $'\r' ]] || [[ $char == $'\n' ]]; then
        # Enter pressed
        stty "$OLD_STTY" 2>/dev/null
        echo
        break
    elif [[ $char == $'\177' ]] || [[ $char == $'\b' ]]; then
        # Backspace
        if [[ -n "$INPUT" ]]; then
            INPUT="${INPUT%?}"
            echo -ne "\b \b"
        fi
    else
        # Normal character - show ASCII code for debugging
        INPUT="${INPUT}${char}"
        echo -n "$char"
        # Debug: show ASCII code
        echo "[ASCII:$ascii]" >&2
    fi
done

# Restore terminal
stty "$OLD_STTY" 2>/dev/null

echo ""
echo "You entered: '$INPUT'"
echo "Length: ${#INPUT}"
echo ""

# Show each character with ASCII code
echo "Character breakdown:"
for (( i=1; i<=${#INPUT}; i++ )); do
    c="${INPUT:$i-1:1}"
    ascii=$(printf '%d' "'$c")
    echo "  Position $i: '$c' (ASCII: $ascii)"
done
