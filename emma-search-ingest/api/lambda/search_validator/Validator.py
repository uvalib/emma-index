from os import path
import regex
import yaml
from shared.helpers import exists, get_multi_param


class Validator:
    """
    Validates the incoming search parameters
    """
    MINIMUM_PARAMS = {'q', 'creator', 'title', 'identifier', 'format', 'formatFeature', 'accessibilityFeature'}
    OPEN_API_SCHEMA_VERSION = '0.0.6'

    def __init__(self, query_string_params, multi_string_params):

        yaml_filename = 'common-domain-'+ self.OPEN_API_SCHEMA_VERSION +'.schema.yaml'
        yaml_file = yaml_filename if path.exists(
            yaml_filename) else '../schema/shared/model/' + yaml_filename

        # Load lists for validation from schema YAML
        with open(yaml_file) as fp:
            yaml_enums = yaml.load(fp, Loader=yaml.SafeLoader)
        schema_org_enums = yaml_enums['components']['schemas']['SchemaOrgFields']['properties']
        emma_enums = yaml_enums['components']['schemas']['EmmaCommonFields']['properties']

        self.VALID_FORMATS = yaml_enums['components']['schemas']['DublinCoreFormat']['enum']
        self.VALID_SORTS = ['title', 'lastRemediationDate', 'sortDate', 'publicationDate']
        self.VALID_GROUPS = yaml_enums['components']['schemas']['Group']['enum']
        self.VALID_REPOSITORIES = yaml_enums['components']['schemas']['EmmaRepository']['enum']
        self.VALID_ACCESSIBILITY_FEATURES = schema_org_enums['s_accessibilityFeature']['items']['enum']
        self.VALID_FORMAT_FEATURES = emma_enums['emma_formatFeature']['items']['enum']

        self.multi_string_params = multi_string_params
        self.query_string_params = query_string_params

    def validate(self, errors):
        """
        Validate the incoming parameters and update the error list
        """
        if not self.query_string_params:
            errors.append("Please include at least the q, creator, title, identifier, format, formatFeature, "
                          "or accessibilityFeature parameter in your request.")
            return

        minimum_params = self.MINIMUM_PARAMS.intersection(self.query_string_params)

        if len(minimum_params) < 1:
            errors.append("Please include at least the q, creator, title, identifier, format, formatFeature, "
                          "or accessibilityFeature parameter in your request.")

        self.validate_query_combinations(errors)
        self.if_exists_validate_param("group", self.VALID_GROUPS, errors)
        self.if_exists_validate_param("repository", self.VALID_REPOSITORIES, errors)
        self.if_exists_validate_param("sort",  self.VALID_SORTS, errors)
        self.if_exists_validate_multi_param('format', self.VALID_FORMATS, errors)
        self.if_exists_validate_multi_param('formatFeature', self.VALID_FORMAT_FEATURES, errors)
        self.if_exists_validate_multi_param('accessibilityFeature', self.VALID_ACCESSIBILITY_FEATURES, errors)
        self.if_exists_is_numeric('from', errors)
        self.if_exists_is_numeric('size', errors)
        self.validate_date('sortDate', errors)
        self.validate_date('lastRemediationDate', errors)
        self.validate_date_or_year('publicationDate', errors)
        self.validate_too_many_records(errors)

    def validate_too_many_records(self, errors):
        """
        Throw an error if the user tries to get more than 1000 records from a relevance query.
        """
        from_int = 0
        size_int = 0
        if exists(self.query_string_params, 'size'):
            size_str = self.query_string_params['size']
            size_int = int(size_str)
        if exists(self.query_string_params, 'from'):
            from_str = self.query_string_params['from']
            from_int = int(from_str)

        if from_int + size_int > 1000:
            errors.append("Only up to 1000 records can be retrieved from a relevance query.")

    def validate_query_combinations(self, errors):
        """
        Enforce query rules with error information
        """
        if (exists(self.query_string_params, 'searchAfterId') \
            and not exists(self.query_string_params, 'searchAfterValue')) \
                or (not exists(self.query_string_params, 'searchAfterId') \
                    and exists(self.query_string_params, 'searchAfterValue')):
            errors.append(
                "searchAfterId and searchAfterValue parameters must either both be present or neither be present.")

        if exists(self.query_string_params, 'sort') and exists(self.query_string_params, 'from'):
            errors.append("The sort parameter cannot be used with the from parameter."
                          "  It should be used with searchAfterId and searchAfterValue when paging.")

        if exists(self.query_string_params, 'searchAfterId') and exists(self.query_string_params, 'group'):
            errors.append("The group parameter cannot be used with the searchAfterId parameter.")

        if not exists(self.query_string_params, 'sort') and (exists(self.query_string_params, 'searchAfterId') \
                                                             or exists(self.query_string_params, 'searchAfterValue')):
            errors.append("The searchAfterId and searchAfterValue parameters require the sort parameter.")

    @staticmethod
    def validate_param(parameter_name, parameter, valid_list, errors):
        """
        Validate a single parameter against a list of valid values.  If the parameter is not valid,
        an error is added to the errors array.
        """
        if parameter not in valid_list:
            display_list = ', '.join(valid_list)
            errors.append(parameter_name + " " + parameter +
                          " not in accepted list " + display_list)

    def if_exists_validate_param(self, parameter_name, valid_list, errors):
        """
        Only validate this parameter if it exists
        """
        if exists(self.query_string_params, parameter_name):
            param_value = self.query_string_params[parameter_name]
            Validator.validate_param(parameter_name, param_value, valid_list, errors)

    def if_exists_validate_multi_param(self, param_name, valid_list, errors):
        """
        If these multi-value parameters exist, validate them.
        For parameters that can have multiple values, get them from the correct API gateway list, validate, and
        add to search filters
        """
        if exists(self.query_string_params, param_name):
            value_list = get_multi_param(param_name, self.query_string_params, self.multi_string_params)
            if value_list is not None:
                for param_value in value_list:
                    Validator.validate_param(param_name, param_value, valid_list, errors)

    def if_exists_is_numeric(self, parameter_name, errors):
        """
        Make sure a parameter is numeric if it exists.
        """
        if exists(self.query_string_params, parameter_name):
            param_value = self.query_string_params[parameter_name]
            if not param_value.isnumeric():
                errors.append(parameter_name + " " + param_value +
                              " should be an integer.")

    def validate_date(self, param_name, errors):
        """
        Validate incoming dates to be IS0-8601 compliant.
        """
        if exists(self.query_string_params, param_name):
            date_param = self.query_string_params[param_name]
            if not regex.match(r'\d{4}-\d{2}-\d{2}', date_param):
                errors.append(date_param + " is not a valid YYYY-MM-DD date")

    def validate_date_or_year(self, param_name, errors):
        """
        Validate incoming dates to be IS0-8601 compliant.
        """
        if exists(self.query_string_params, param_name):
            date_param = self.query_string_params[param_name]
            if not regex.match(r'\d{4}-\d{2}-\d{2}', date_param)\
                    and not regex.match(r'\d{4}', date_param):
                errors.append(date_param + " is not a valid YYYY year or YYYY-MM-DD date")