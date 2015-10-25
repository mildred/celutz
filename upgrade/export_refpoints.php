<?php

/* Converts a set of refpoints to a JSON file suitable for Django import. */

/* Pass one or several refpoint PHP files as arguments. */

function convert_refpoints($refpoint_file) {
    $ref_points = array();
    include($refpoint_file);
    $result = array();
    foreach ($ref_points as $name => $attributes) {
        $item = array("model" => "panorama.referencepoint");
        $item["fields"] = array("name" => $name,
                                "latitude" => $attributes[0],
                                "longitude" => $attributes[1],
                                "altitude" => $attributes[2]);
        $result[] = $item;
    }
    return $result;
}

function convert_all_refpoints($argv) {
    $all_refpoints = array();
    foreach (array_slice($argv, 1) as $refpoint_file) {
        $all_refpoints = array_merge($all_refpoints, convert_refpoints($refpoint_file));
    }
    print(json_encode($all_refpoints, JSON_PRETTY_PRINT));
}

if (isset($argv[1])) {
    convert_all_refpoints($argv);
} else {
    printf("Usage: %s <ref_points_1.php> [ref_points_2.php [...]]\n", $argv[0]);
}

?>