from functools import wraps


def f_main(args=None):
    """
    Decorator to be used for all the main function .
    It performs some standard operation like:
        - updates (or merges) cmd_line args with parms from config_file
        - obtain loss values from the model
        - save experiment's artifact (model's weights)
        - save experiment's results
    """
    def callable_wrapper(main_func):
        @wraps(main_func)  # Tells debuggers that is is a function wrapper
        def decorator(ex, _run, f_log_metrics):
            # Override argparse arguments with sacred arguments (from yaml)
            vars(args).update(_run.config)

            # call main script
            val_loss, test_loss, model_name = main_func(_run)
            print('--------- TEST RESULTS ---------------')
            print(test_loss)
            print('--------------------------------------')
            csv_loss = ', '.join([str(round(v, 10)) for (_, v) in test_loss.items()])
            with open('experiment_results.csv', 'a') as f:
                f.write(csv_loss + '\n')

            # save the result metrics to db
            _run.info['model_metrics'] = dict(val_loss=val_loss, test_loss=test_loss)
            # save an artifact (keras model) to db
            if isinstance(model_name, str):
                ex.add_artifact(model_name)
            else:
                for m in model_name:
                    ex.add_artifact(m)
            return test_loss

        return decorator

    return callable_wrapper
