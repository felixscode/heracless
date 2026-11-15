//! Turning arbitrary YAML keys into valid Python identifiers.

/// Python keywords, which can't be used as attribute or class names.
const PYTHON_KEYWORDS: &[&str] = &[
    "False", "None", "True", "and", "as", "assert", "async", "await", "break", "class", "continue",
    "def", "del", "elif", "else", "except", "finally", "for", "from", "global", "if", "import",
    "in", "is", "lambda", "nonlocal", "not", "or", "pass", "raise", "return", "try", "while",
    "with", "yield",
];

pub fn is_python_keyword(name: &str) -> bool {
    PYTHON_KEYWORDS.contains(&name)
}

/// Split a key into words on non-alphanumeric characters and case boundaries.
///
/// Acronyms stay together: `HTTPServer` -> `HTTP`, `Server`; digits stick to the
/// preceding word: `ipv4Address` -> `ipv4`, `Address`.
pub fn split_words(key: &str) -> Vec<&str> {
    let mut words = Vec::new();
    let chars: Vec<(usize, char)> = key.char_indices().collect();
    let mut start: Option<usize> = None;

    for (i, &(pos, c)) in chars.iter().enumerate() {
        if !c.is_ascii_alphanumeric() {
            if let Some(s) = start.take() {
                words.push(&key[s..pos]);
            }
            continue;
        }
        if let Some(s) = start {
            let prev = chars[i - 1].1;
            let next = chars.get(i + 1).map(|&(_, n)| n);
            let boundary = c.is_ascii_uppercase()
                && (prev.is_ascii_lowercase()
                    || prev.is_ascii_digit()
                    || (prev.is_ascii_uppercase() && next.is_some_and(|n| n.is_ascii_lowercase())));
            if boundary {
                words.push(&key[s..pos]);
                start = Some(pos);
            }
        } else {
            start = Some(pos);
        }
    }
    if let Some(s) = start {
        words.push(&key[s..]);
    }
    words
}

/// Make `name` a usable identifier: no leading digit, not a keyword.
fn finish_identifier(mut name: String, leading_underscore: bool, fallback: &str) -> String {
    if name.is_empty() {
        name = fallback.to_string();
    }
    if leading_underscore || name.starts_with(|c: char| c.is_ascii_digit()) {
        name.insert(0, '_');
    }
    if is_python_keyword(&name) {
        name.push('_');
    }
    name
}

/// Attribute name for a key: `bill-to` -> `bill_to`, `apiKey` -> `api_key`, `class` -> `class_`.
pub fn to_snake_case(key: &str) -> String {
    let snake = split_words(key)
        .iter()
        .map(|w| w.to_ascii_lowercase())
        .collect::<Vec<_>>()
        .join("_");
    finish_identifier(snake, key.starts_with('_'), "field")
}

/// Class name for a key: `bill-to` -> `BillTo`, `HTTPServer` -> `HttpServer`.
pub fn to_pascal_case(key: &str) -> String {
    let pascal: String = split_words(key)
        .iter()
        .map(|w| {
            let lower = w.to_ascii_lowercase();
            let mut chars = lower.chars();
            match chars.next() {
                Some(first) => first.to_ascii_uppercase().to_string() + chars.as_str(),
                None => String::new(),
            }
        })
        .collect();
    finish_identifier(pascal, false, "Field")
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn splits_words() {
        assert_eq!(split_words("bill-to"), ["bill", "to"]);
        assert_eq!(split_words("HTTPServer"), ["HTTP", "Server"]);
        assert_eq!(split_words("ipv4Address"), ["ipv4", "Address"]);
        assert_eq!(split_words("v2Beta"), ["v2", "Beta"]);
        assert_eq!(split_words("__a..b__"), ["a", "b"]);
        assert!(split_words("-").is_empty());
    }

    #[test]
    fn snake_case() {
        assert_eq!(to_snake_case("TestName"), "test_name");
        assert_eq!(to_snake_case("test-name"), "test_name");
        assert_eq!(to_snake_case("test.name"), "test_name");
        assert_eq!(to_snake_case("UPPER_CASE"), "upper_case");
        assert_eq!(to_snake_case("apiKey"), "api_key");
        assert_eq!(to_snake_case("myKey2Value"), "my_key2_value");
        assert_eq!(to_snake_case("class"), "class_");
        assert_eq!(to_snake_case("1start"), "_1start");
        assert_eq!(to_snake_case("_private"), "_private");
        assert_eq!(to_snake_case("größe"), "gr_e");
        assert_eq!(to_snake_case(""), "field");
    }

    #[test]
    fn pascal_case() {
        assert_eq!(to_pascal_case("bill-to"), "BillTo");
        assert_eq!(to_pascal_case("product_item"), "ProductItem");
        assert_eq!(to_pascal_case("HTTPServer"), "HttpServer");
        assert_eq!(to_pascal_case("none"), "None_");
        assert_eq!(to_pascal_case("2fa"), "_2fa");
    }
}
