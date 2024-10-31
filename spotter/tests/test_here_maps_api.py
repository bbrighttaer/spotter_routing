import pytest

from spotter.truck_routing.services import here_maps


@pytest.mark.parametrize("query", [("WOODSHED OF BIG CABIN",), ("KWIK TRIP #796",)])
def test_geocoding(query):
    response = here_maps.geocode(query)
    assert len(response) > 0


@pytest.mark.parametrize(
    "start_coordinates, end_coordinates", [("52.5308,13.3847", "52.5264,13.3686")]
)
def test_get_route(start_coordinates, end_coordinates):
    start_coordinates = start_coordinates.split(",")
    end_coordinates = end_coordinates.split(",")
    response = here_maps.get_route(
        start_coordinates={
            "latitude": start_coordinates[0],
            "longitude": start_coordinates[1],
        },
        finish_coordinates={
            "latitude": end_coordinates[0],
            "longitude": end_coordinates[1],
        },
    )
    assert len(response) > 0


@pytest.mark.parametrize("start_coordinates", ["52.5308,13.3847"])
def test_get_gas_stations_along_route(start_coordinates):
    start_coordinates = start_coordinates.split(",")
    response = here_maps.get_gas_stations_along_route(
        start_coordinates={
            "latitude": start_coordinates[0],
            "longitude": start_coordinates[1],
        },
        route="BF-hw4Hzw2jOwyH51kB2uU77gBwjC3vSomI_6J1hEh0iB69Gl7TsP7t7B8wNhuK_gC_"
        "zRsgFrqMqwI3lEuzDjuP64BrtsBvrFzmTyQv_pB34K_5qBssB_wamxF_wMjqKzylC-3"
        "RzmqBjiH5goBm3Ex5P7pDpvUskE5-Q5lKxgiBxpJnpLj-E55Qy2Pz_jBhlM_7lB-9Lzm"
        "zBwlUzynBzcv0V4jHlvc1hE9-boqG15Ik9DrmnBvtDlsNw-Ev8jC9yFjoOi7G3irBx5D1"
        "vzD_wOvz9B-sZttfuqCt1zD0hUrw5BwjHr5vBhiDl1atkInyVp2Bn2d2rFlokCo2KvuzB-"
        "zjBh1iD1SzgpEo-Hxy7C-7U3qgBuoE5tvBz_HjyhGu5Hv1wB98F7lbn_J_pO5mUl_8BkqE"
        "jswBlhFh_PshDn2rC5jGl3OiDzjajsHp0Rpczpbx9J59gBh1Pzjar5C79uEo_G_zb53C5igDm"
        "-FjpZxoCpxL6-G30jBgC5kiBiqEp7G5lDzilB2sLt-RkgT9oB--F7ufk9L3t1Ev3C7olI67Dz"
        "q0BlyJ_ppCiCj-jBluLv4Cp-Nv83B5VltXhzEh6GsbjipIjyKx5E_opB74rBr7B5vyB__"
        "Q11P95KtoV_xOhhH_6SlqiB54Cl3iBtyPlsSyuBr8gKz9Szm0BziLn6jC0vHpt-D0z2Bju"
        "9DkmX_hzC20GxkkCnlHn-rCmhChyzBjrPnwuCrlTxlgB5rCn-bznhBnwnDl1Tl8gBvwwBvqo"
        "Bn0Z92rBnvI1o0DvhZpl0Cn41BhujCj1J5mmBxoQvvN-4N_4xCr-NtjTmrB70ahiM72jB7-ax"
        "lXwnBjlH6nQ91Iu4K19M5G3rPtmH13L-tJrojBo6KxwN5oLt5aj4Bx-uBhlRnugB6xCvh4B_5"
        "Jp79B7iJr7hB58Tv2ch5Vp5R35J2Nh_RpiOn1B_7_B6hYx3xB77HxpT5b5wUp3xBly8B4zFr7"
        "5BriI1lsB26N1muB_pNtvlBg7CviVp3E7sElhJninBruFz3sC3uQh_4BytBphOqrI99Mq_NlzF"
        "u4Kr77BvvcjosBlwVh9Nj6SpsXjZp2MrzFh6F-8Lrta9qGxwSpiUvsBx0Tj1J_liBslD3sK2_F_"
        "tN56NzypB98al4clivB3mNnkEzkG_vM19O9qKv1YjiGr4YtzNv0U_kW5hNt8ariYj-N7iHzohB9"
        "yHtyHyIv0H16Qtga55Ml9f24Cv_Rl8Gl_ehlOxiT75BjmKh8lB72xBtsb5mT3qTrmlBziTn2M_z"
        "kB5Xz4mB_lhBx31B_gTkWv6azyUj7-B_pWhziBrtKlwGtnTr3br0E14a3sdtl_B37I5niCt0OvkHv"
        "0QzvS_gPxwEhxgBp8XrwYl2T1hCvhItoR2oGpsGs1HllQpoQnqExvnCgrD79SnwNj_I1oC3uvB",
    )
    assert len(response) > 0
