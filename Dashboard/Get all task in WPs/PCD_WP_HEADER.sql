SELECT
    wpno_i,
    wpno,
    ac_registr AS "AC_REG",
    station AS "STATION",
    TO_CHAR(DATE '1971-12-31' + start_date, 'DD.MON.YYYY') AS "START_DATE",
    TO_CHAR(TIME '00:00' + (start_time || ' minutes')::interval, 'HH24:MI') AS "START_TIME",
    TO_CHAR(DATE '1971-12-31' + end_date, 'DD.MON.YYYY') AS "END_DATE",
    TO_CHAR(TIME '00:00' + (end_time || ' minutes')::interval, 'HH24:MI') AS "END_TIME",
    TO_CHAR(TIME '00:00' + (
        CASE
            WHEN end_time < start_time THEN (end_time + 1440) - start_time
            ELSE end_time - start_time
            END || ' minutes')::interval, 'HH24:MI') AS "GROUND_TIME",
    remarks AS "REMARKS"
FROM
    wp_header
WHERE
    wp_header.wpno_i IN (@VAR.WP@)

ORDER BY
    CASE
        WHEN wp_header.station = 'SGN' THEN 1
        WHEN wp_header.station = 'HAN' THEN 2
        WHEN wp_header.station = 'DAD' THEN 3
        WHEN wp_header.station = 'CXR' THEN 4
        WHEN wp_header.station = 'HPH' THEN 5
        WHEN wp_header.station = 'VII' THEN 6
        WHEN wp_header.station = 'VCA' THEN 7
        WHEN wp_header.station = 'PQC' THEN 8
        ELSE 9
        END,
    wp_header.ac_registr