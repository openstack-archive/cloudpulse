#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.


from cloudpulse.common import exception
from cloudpulse.common.plugin import discover
import itertools


def scenario(admin_only=False, operator=False, context=None):
    """Add extra fields to benchmark scenarios methods.

       This method is used as decorator for the methods of benchmark scenarios
       and it adds following extra fields to the methods.

       'is_scenario' is set to True
       'admin_only' is set to True if a scenario require admin endpoints
       'operator' is set to True if the scenario is an operator scenario
    """

    def wrapper(func):
        func.is_scenario = True
        func.admin_only = admin_only
        func.operator = operator
        func.context = context or {}
        return func
    return wrapper


class Scenario(object):
    """This is base class for any benchmark scenario.

       You should create subclass of this class. And your test scenarios will
       be auto discoverable and you will be able to specify it in test config.
    """
    def __init__(self, context=None, admin_tests=None,
                 tenant_tests=None, operator_tests=None):
        self._admin_tests = admin_tests
        self.tenant_tests = tenant_tests
        self.operator_tests = operator_tests

    @staticmethod
    def get_by_name(name):
        """Returns Scenario class by name."""
        for scenario in discover.itersubclasses(Scenario):
            if name == scenario.__name__:
                return scenario
        raise exception.NoSuchScenario(name=name)

    @staticmethod
    def is_scenario(cls, method_name):
        """Check whether a given method in scenario class is a scenario.

        :param cls: scenario class
        :param method_name: method name

        :returns: True if the method is a benchmark scenario, False otherwise
        """
        try:
            getattr(cls, method_name)
        except Exception:
            return False
        return Scenario.meta(cls, "is_scenario", method_name, default=False)

    @staticmethod
    def is_admin(cls, method_name):
        """Check whether a given method in scenario class is a scenario.

        :param cls: scenario class
        :param method_name: method name

        :returns: True if the method is a benchmark scenario, False otherwise
        """
        try:
            getattr(cls, method_name)
        except Exception:
            return False
        return Scenario.meta(cls, "admin_only", method_name, default=False)

    @staticmethod
    def is_operator(cls, method_name):
        """Check whether a given method in scenario class is a scenario.

        :param cls: scenario class
        :param method_name: method name

        :returns: True if the method is a benchmark scenario, False otherwise
        """
        try:
            getattr(cls, method_name)
        except Exception:
            return False
        return Scenario.meta(cls, "operator", method_name, default=False)

    @classmethod
    def list_operator_scenarios(scenario_cls):
        """Lists all the existing methods in the operator scenario classes.

        Returns the method names in format <Class name>.<Method name>, which
        is used in the test config.

        :returns: List of strings
        """
        scenario_classes = (list(discover.itersubclasses(scenario_cls)) +
                            [scenario_cls])
        scenarios_list = [
            ["%s.%s" % (scenario.__name__, func)
             for func in dir(scenario)
             if Scenario.is_scenario(scenario, func)
             and Scenario.is_operator(scenario, func)]
            for scenario in scenario_classes
        ]
        operator_scenarios = list(
            itertools.chain.from_iterable(scenarios_list))
        return operator_scenarios

    @classmethod
    def list_admin_scenarios(scenario_cls):
        """Lists all the existing methods in the operator scenario classes.

        Returns the method names in format <Class name>.<Method name>, which
        is used in the test config.

        :returns: List of strings
        """
        scenario_classes = (list(discover.itersubclasses(scenario_cls)) +
                            [scenario_cls])
        scenarios_list = [
            ["%s.%s" % (scenario.__name__, func)
             for func in dir(scenario)
             if Scenario.is_scenario(scenario, func) and
             Scenario.is_admin(scenario, func)]
            for scenario in scenario_classes
        ]
        scenarios_list_admin = list(
            itertools.chain.from_iterable(scenarios_list))
        return scenarios_list_admin

    @classmethod
    def list_tenant_scenarios(scenario_cls):
        """Lists all the existing methods in the operator scenario classes.

        Returns the method names in format <Class name>.<Method name>, which
        is used in the test config.

        :returns: List of strings
        """
        scenario_classes = (list(discover.itersubclasses(scenario_cls)) +
                            [scenario_cls])
        scenarios_list = [
            ["%s.%s" % (scenario.__name__, func)
             for func in dir(scenario)
             if Scenario.is_scenario(scenario, func) and
             not Scenario.is_admin(scenario, func) and
             not Scenario.is_operator(scenario, func)]
            for scenario in scenario_classes
        ]
        tenant_scenarios = list(
            itertools.chain.from_iterable(scenarios_list))
        return tenant_scenarios

    @classmethod
    def list_all_scenarios(scenario_cls):
        """Lists all the existing methods in the operator scenario classes.

        Returns the method names in format <Class name>.<Method name>, which
        is used in the test config.

        :returns: List of strings
        """
        scenario_classes = (list(discover.itersubclasses(scenario_cls)) +
                            [scenario_cls])
        scenarios_list = [
            ["%s.%s" % (scenario.__name__, func)
             for func in dir(scenario) if Scenario.is_scenario(scenario, func)]
            for scenario in scenario_classes
        ]
        scenarios_list_flat = list(
            itertools.chain.from_iterable(scenarios_list))
        return scenarios_list_flat

    @classmethod
    def validate(cls, name, config, admin=None, users=None, task=None):
        """Semantic check of benchmark arguments."""
        if cls.meta(name, "admin_only") is True:
            print("Admin Access")
        if cls.meta(name, "operator") is True:
            print("Operator")

    def setup(self, *args, **kwargs):
        """TODO:Implement setup and teardown"""
        pass

    def teardown(self, *args, **kwargs):
        """TODO:Implement setup and teardown"""
        pass

    @staticmethod
    def meta(cls, attr_name, method_name=None, default=None):
        """Extract the named meta information out of the scenario name.

        :param cls: Scenario (sub)class or string of form 'class.method'
        :param attr_name: Name of method attribute holding meta information.
        :param method_name: Name of method queried for meta information.
        :param default: Value returned if no meta information is attached.

        :returns: Meta value bound to method attribute or default.
        """
        if isinstance(cls, str):
            cls_name, method_name = cls.split(".", 1)
            cls = Scenario.get_by_name(cls_name)
        method = getattr(cls, method_name)
        return getattr(method, attr_name, default)
