<?php

/* Converts a panorama to a dictionary with all parameters. */
/* Given "foo.tif", fetch parameters from "tiles/foo/site.params" */
function load_panorama($image_name) {
    $components = pathinfo($image_name);
    $celutz_dir = pathinfo($components["dirname"])["dirname"];
    $params_file = join("/", array($celutz_dir, "tiles", $components["filename"], "site.params"));
    $params = parse_ini_file($params_file);
    if (! $params)
        return false;
    $result = array();
    $result["loop"] = (boolean) $params["image_loop"];
    $result["name"] = $params["titre"];
    // Relative to Django's MEDIAROOT
    $result["image"] = "pano/" . $components["basename"];
    $result["latitude"] = (float) $params["latitude"];
    $result["longitude"] = (float) $params["longitude"];
    $result["altitude"] = (float) $params["altitude"];
    return $result;
}

/* Convert all panoramas images found in the given directory to JSON */
function convert_panoramas($upload_dir) {
    /* The Django model uses inheritance, so we need to create both the
     * panorama and the associated reference point, with the same ID. */
    $panoramas = array();
    $refpoints = array();
    $id = 1;
    foreach (scandir($upload_dir) as $pano) {
        if ($pano == "." || $pano == "..")
            continue;
        $params = load_panorama($upload_dir . "/" . $pano);
        if (! $params)
            continue;
        $p = array("pk" => $id, "model" => "panorama.panorama");
        $r = array("pk" => $id, "model" => "panorama.referencepoint");
        $p["fields"] = array("loop" => $params["loop"], "image" => $params["image"]);
        $r["fields"] = array("name" => $params["name"],
                             "latitude" => $params["latitude"],
                             "longitude" => $params["longitude"],
                             "altitude" => $params["altitude"]);
        $panoramas[] = $p;
        $refpoints[] = $r;
        $id++;
    }
    return json_encode(array_merge($panoramas, $refpoints), JSON_PRETTY_PRINT);
}

if (isset($argv[1])) {
    print(convert_panoramas($argv[1] . "/upload"));
} else {
    printf("Usage: %s /path/to/celutz\n", $argv[0]);
}

?>