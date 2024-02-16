"""Helper class to convert types and check against to IOTC standards"""

class IOTCTypes:
    """Helper class to convert types and check against to IOTC standards"""
    # No way to get this from the API atm
    guids = {
        "BIT": "C2B509B5-8883-46CD-861F-11B460E7F7AD",
        "BOOLEAN": "BA95C16E-5DE4-4066-BA85-E79FB833839C",
        "DATE": "63D9F444-B37D-4C0E-87A5-45C3AED0B724",
        "DATETIME": "CEBBFDB9-AD6E-47D2-85E2-9F290079386B",
        "DECIMAL": "0C19A49A-31A6-452E-B94B-3ECC253B3F29",
        "INTEGER": "3D1B3160-9E69-4584-921E-C654682C1BD9",
        "LATLONG": "D2E69AEB-953E-4E72-9B72-9AF24FD075F0",
        "LONG": "F808D5B7-EE48-44A7-86BD-CC879A652BA4",
        "OBJECT": "3D165C3D-2E97-4E8C-BE11-6F49D167CC07",
        "STRING": "01B2B63B-7BC7-4D9D-8152-8E6298C878DE",
    }

    @classmethod
    def to_guid(cls, obj):
        """
        attempts to set the template attribute type
        :param obj: object
        :return string:
        """
        if isinstance(obj, str):
            return cls.guids["STRING"]

        elif isinstance(obj, bool):
            return cls.guids["BOOLEAN"]

        elif isinstance(obj, float):
            return cls.guids["DECIMAL"]

        elif isinstance(obj, int):
            # or isinstance(obj, numbers.Integral)
            # return cls.guids["INTEGER"]  # will cause error if obj is a float at integer value at instantiation
            return cls.guids["DECIMAL"]

        elif isinstance(obj, dict):
            return cls.guids["OBJECT"]

        elif isinstance(obj, str):
            return cls.guids["STRING"]

        # elif isinstance(obj, datetime):
        #     return cls.data_types['DATETIME']

        # elif isinstance(obj, bit):
        #     return cls.data_types['BIT']

        elif cls.is_lat_long(obj):
            return cls.guids["LATLONG"]

        # elif isinstance(obj, type):
        #     return cls.data_types['DATE']

        # elif isinstance(obj, type):
        #     return cls.data_types['TIME']

        return cls.guids["STRING"]

    @classmethod
    def to_lat_long(cls, latitude, longitude):
        return [float(f"{latitude:10.8f}"), float(f"{longitude:11.8f}")]

    @classmethod
    def is_lat_long(cls, list_object):
        return bool(
            len(list_object) == 2
            and list_object[0] == float(f"{list_object[0]:10.8f}")
            and list_object[1] == float(f"{list_object[1]:11.8f}")
        )
