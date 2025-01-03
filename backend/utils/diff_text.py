from difflib import SequenceMatcher
from utils.general import linearize_transcript


def cleaned(s: str) -> str:
    JUNK_CHARS = "".join(
        (",", ".", ";", ":", '"', "'", "-", ")", "(", "[", "]", "{", "}", "?", "!")
    )

    if len(s) == 0:
        return s
    orig_s = s
    s = s.lower()
    s = s.translate(str.maketrans("", "", JUNK_CHARS))
    return s


def diff_text(paragraph1: str, paragraph2: str, print_result: bool = True):
    def _print_diff_colored(p1, p2, opcodes):
        formatted_paragraph = ""
        for opcode in opcodes:
            # (tag, i1, i2, j1, j2) = opcode
            # print("%s paragraph1[%d:%d] (%s) paragraph2[%d:%d] (%s)" % (tag, i1, i2, ' '.join(p1[i1:i2]), j1, j2, ' '.join(p2[j1:j2])))

            if opcode[0] == "equal":
                # No change in this segment, just add it to both formatted paragraphs
                formatted_paragraph += " ".join(p1[opcode[1] : opcode[2]])
            elif opcode[0] == "delete":
                # This segment was removed in the second paragraph, color it red in the first paragraph
                formatted_paragraph += (
                    " \033[31m" + " ".join(p1[opcode[1] : opcode[2]]) + "\033[0m "
                )
            elif opcode[0] == "replace":
                # This segment was replaced in the first paragraph, color it red in the first paragraph and green in the second
                formatted_paragraph += (
                    " (\033[33m" + " ".join(p1[opcode[1] : opcode[2]]) + "\033[0m ->"
                )
                formatted_paragraph += (
                    "\033[34m" + " ".join(p2[opcode[3] : opcode[4]]) + "\033[0m) "
                )
            elif opcode[0] == "insert":
                # This segment was added in the second paragraph, color it green in the second paragraph
                formatted_paragraph += (
                    " \033[32m" + " ".join(p2[opcode[3] : opcode[4]]) + "\033[0m "
                )
        print(formatted_paragraph)

    # Split them into words by whitespace, so we diff on words instead of letters:
    p1, p2 = paragraph1.split(), paragraph2.split()

    # For each word, there can be punctuation attached. We want to remove the punctuation,
    # -- so that the diff doesn't care about it --but, we also want to keep track of the original
    # words *with* punctuation, so we can reconstruct the sentence.
    p1_orig, p2_orig = p1[:], p2[:]
    p1 = [cleaned(word) for word in p1]
    p2 = [cleaned(word) for word in p2]

    # Diff on words, using difflib:
    s = SequenceMatcher(None, p1, p2)
    opcodes = s.get_opcodes()

    # Print the diff with added words in green and removed words in red
    if print_result is True:
        _print_diff_colored(p1, p2, opcodes)

    return opcodes


def hallucination_rate(original, summary):
    opcodes = diff_text(original, summary, False)
    replace_opcodes = [opcode for opcode in opcodes if opcode[0] == "replace"]

    num_words_replaced = sum([opcode[2] - opcode[1] for opcode in replace_opcodes])

    return num_words_replaced / len(summary.split())


def revert_hallucinations(original, summary):
    p1 = original.split()
    p2 = summary.split()

    # Diff on words, using difflib:
    opcodes = diff_text(original, summary, False)
    rst = ""
    for code in opcodes:
        if code[0] == "equal":
            rst += " ".join(p2[code[3] : code[4]]) + " "
        elif code[0] == "replace":
            rst += " ".join(p1[code[1] : code[2]]) + " "

    return rst


def revert_internal_deletions(original, summary):
    # Diff on words, using difflib:
    opcodes = diff_text(original, summary, False)

    # Get the first and last "equal" opcodes from the diff
    first_equal_opcode = next((x for x in opcodes if x[0] == "equal"), None)
    last_equal_opcode = next((x for x in reversed(opcodes) if x[0] == "equal"), None)

    # If there is only one equal opcode, then there are no internal deletions, so, return
    if (
        first_equal_opcode[1] == last_equal_opcode[1]
        and first_equal_opcode[2] == last_equal_opcode[2]
    ):
        return summary

    # Calculate the new range
    new_range = (first_equal_opcode[1], last_equal_opcode[2])

    return " ".join(original.split(" ")[first_equal_opcode[1] : last_equal_opcode[2]])


def find_section_range(transcript, section):
    # Convert transcript to text
    transcript_text = linearize_transcript(transcript)

    # Strip
    section = section.strip()

    # Check how much it has hallucinated
    # If it has hallucinated a LOT (e.g. just created random text), then discard it - we could not find a match
    if hallucination_rate(transcript_text, section) > 0.1:
        return None

    # Revert hallucinations
    section = revert_hallucinations(transcript_text, section)
    section = revert_internal_deletions(transcript_text, section)

    # Get diff
    opcodes = diff_text(transcript_text, section, False)

    # Get "equal" opcode, i.e. where there is a match
    equal_opcode = next((x for x in opcodes if x[0] == "equal"), None)
    if equal_opcode == None:
        return None

    # Get start and end word index
    start_word_index = equal_opcode[1]
    end_word_index = equal_opcode[2] - 1

    return start_word_index, end_word_index + 1
