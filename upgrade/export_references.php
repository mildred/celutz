<?php

/* Loads all references for the given panorama into a dictionary */
function load_references($image_name) {
    $components = pathinfo($image_name);
    $celutz_dir = pathinfo($components["dirname"])["dirname"];
    $params_file = join("/", array($celutz_dir, "tiles", $components["filename"], "site.params"));
    $params = parse_ini_file($params_file);
    if (! $params)
        return false;
    $res = array();
    if (! isset($params["reference"]))
        return $res;
    foreach ($params["reference"] as $name => $position) {
        $pos = explode(",", $position);
        $res[] = array("pano" => $params["titre"],
                       "refpoint" => $name,
                       "x" => (float) $pos[0],
                       "y" => (float) $pos[1]);
    }
    return $res;
}

function convert_references($upload_dir) {
    $result = array();
    foreach (scandir($upload_dir) as $pano) {
        if ($pano == "." || $pano == "..")
            continue;
        $references = load_references($upload_dir . "/" . $pano);
        if (! $references)
            continue;
        $result = array_merge($result, $references);
    }
    return json_encode($result, JSON_PRETTY_PRINT);
}

if (isset($argv[1])) {
    print(convert_references($argv[1] . "/upload"));
} else {
    printf("Usage: %s /path/to/celutz\n", $argv[0]);
}

?>