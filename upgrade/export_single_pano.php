<?php

/* Loads a single "site.params" file and outputs it to json. */

function load_site_params($filename) {
    $params = parse_ini_file($filename);
    if (! $params)
        return false;
    // Normalise for convenience (otherwise, it's empty string for false
    // and "1" for true...)
    $params["image_loop"] = (boolean) $params["image_loop"];
    return $params;
}

if (isset($argv[1])) {
    $result = load_site_params($argv[1]);
    if (! $result)
        print("Error");
    else
        print(json_encode($result, JSON_PRETTY_PRINT));
} else {
    printf("Usage: %s /path/to/site.params\n", $argv[0]);
}

?>